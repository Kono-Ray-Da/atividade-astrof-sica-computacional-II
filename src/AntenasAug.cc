#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <map>
#include <string>
#include <cmath>
#include <iomanip>
#include <filesystem>
#include <regex>
#include <limits>
#include <algorithm>

using namespace std;

struct Antena_info {
    int ID;
	int ID_arquivo;
    int ingrid;
    double northing, easting;
    double spectro_ch1[24][51];
    double spectro_ch0[24][51];
};

struct posicao{
	double tempo;
	double freq;
	double power;

};

double DesvioPadrao(const vector<double>& valores) {

    int N = valores.size();
    if (N == 0) {
        return 0.0;
    }
    // Calcula a média
    double soma = 0.0;
    for (int i = 0; i < N; i++) {
        soma += valores[i];
    }
    double media = soma / N;

    // Calcula a soma dos quadrados das diferenças
    double somaQuadrados = 0.0;
    for (int i = 0; i < N; i++) {
        somaQuadrados += pow(valores[i] - media, 2);
    }
    // Calcula o desvio padrão populacional
    double desvioPadrao = sqrt(somaQuadrados / N);
    return desvioPadrao;
}

int ValorGrupo(const map<int, int>& grupos, int chave){
    auto it = grupos.find(chave);
    if (it != grupos.end())
        return it->second;

    return 0;
}


void AnaliseEspectro(vector<Antena_info>& Stations) {

    ofstream saida("Analise_Espectros.txt");

    if (!saida.is_open()) {
        cerr << "Erro ao criar arquivo de saida.\n";
        return;
    }

    saida << fixed << setprecision(8);

    saida << "Antena\tLST\tMedia_CH0\tDesvio_Padrao_CH0"
          << "\tMedia_CH1\tDesvio_Padrao_CH1\n";

    for (int Ant = 0; Ant < Stations.size(); Ant++) {

        if (Ant % 100 == 0) {
            cout << "Analisando antena: " << Ant
                 << " de " << Stations.size() << endl;
        }

        vector<double> perfilTemp_ch0;
        vector<double> perfilTemp_ch1;

        for (int t = 0; t < 24; t++) {

            vector<double> valores_ch0;
            vector<double> valores_ch1;

            double soma_ch0 = 0.0;
            double soma_ch1 = 0.0;

            for (int f = 0; f < 50; f++) {

                double pot_ch0 = Stations[Ant].spectro_ch0[t][f];
                double pot_ch1 = Stations[Ant].spectro_ch1[t][f];

                valores_ch0.push_back(pot_ch0);
                valores_ch1.push_back(pot_ch1);

                soma_ch0 += pot_ch0;
                soma_ch1 += pot_ch1;
            }

            // Média
            double media_ch0 = soma_ch0 / 50.0;
            double media_ch1 = soma_ch1 / 50.0;

            // Desvio padrão
            double desvio_ch0 = DesvioPadrao(valores_ch0);
            double desvio_ch1 = DesvioPadrao(valores_ch1);

            // Perfil temporal
            perfilTemp_ch0.push_back(media_ch0);
            perfilTemp_ch1.push_back(media_ch1);

            // Salva os resultados
            saida << Stations[Ant].ID << "\t"
                  << t + 0.5 << "\t"
                  << media_ch0 << "\t"
                  << desvio_ch0 << "\t"
                  << media_ch1 << "\t"
                  << desvio_ch1 << "\n";
        }
    }

    saida.close();

    cout << "Arquivo Analise_Espectros.txt gerado com sucesso!\n";

	ofstream saidaEspectral("Perfil_Espectral.txt");

	if (!saidaEspectral.is_open()) {
		cerr << "Erro ao criar Perfil_Espectral.txt\n";
		return;
	}

	saidaEspectral << fixed << setprecision(8);

	saidaEspectral << "Antena\tFrequencia"
				<< "\tMedia_CH0\tDesvio_CH0"
				<< "\tMedia_CH1\tDesvio_CH1\n";

	for (int Ant = 0; Ant < Stations.size(); Ant++) {

		if (Ant % 100 == 0) {
			cout << "Analisando perfil espectral da antena: "
				<< Ant << " de " << Stations.size() << endl;
		}

		for (int f = 0; f < 50; f++) {

			vector<double> valores_ch0;
			vector<double> valores_ch1;

			double soma_ch0 = 0.0;
			double soma_ch1 = 0.0;

			for (int t = 0; t < 24; t++) {

				double pot_ch0 = Stations[Ant].spectro_ch0[t][f];
				double pot_ch1 = Stations[Ant].spectro_ch1[t][f];

				valores_ch0.push_back(pot_ch0);
				valores_ch1.push_back(pot_ch1);

				soma_ch0 += pot_ch0;
				soma_ch1 += pot_ch1;
			}

			double media_ch0 = soma_ch0 / 24.0;
			double media_ch1 = soma_ch1 / 24.0;

			double desvio_ch0 = DesvioPadrao(valores_ch0);
			double desvio_ch1 = DesvioPadrao(valores_ch1);

			double frequencia = 30.5 + f;

			saidaEspectral << Stations[Ant].ID << "\t"
						<< frequencia << "\t"
						<< media_ch0 << "\t"
						<< desvio_ch0 << "\t"
						<< media_ch1 << "\t"
						<< desvio_ch1 << "\n";
		}
	}

	saidaEspectral.close();
} // fim do void AnaliseEspectro

void Posicoes(vector<Antena_info>& Stations) {

    // ============================================================
    // 1. Contagem de antenas por configuração
    // ============================================================

    map<int, int> grupos;

    int SD1500 = 0;
    int SD750 = 0;
    int SD433 = 0;

    for (int Ant = 0; Ant < Stations.size(); Ant++) {

        int grupo = Stations[Ant].ingrid;
        grupos[grupo]++;

        if (grupo == 1)
            SD1500++;
        else if (grupo == 2)
            SD750++;
        else if (grupo == 3)
            SD433++;
    }

    cout << "SD-1500: " << SD1500 << endl;
    cout << "SD-750: " << SD750 << endl;
    cout << "SD-433: " << SD433 << endl;

    cout << "\nDistribuicao das configuracoes:\n";

    for (const auto& grupo : grupos) {
        cout << "inGrid " << grupo.first << ": "
             << grupo.second << " antenas\n";
    }


    // ============================================================
    // 2. Média de potência por configuração de malha
    // ============================================================

    map<int, double> soma_CH0;
    map<int, double> soma_CH1;

    map<int, int> quantidade_CH0;
    map<int, int> quantidade_CH1;

    for (int Ant = 0; Ant < Stations.size(); Ant++) {

        int grupo = Stations[Ant].ingrid;

        for (int t = 0; t < 24; t++) {
            for (int f = 0; f < 50; f++) {

                double p0 = Stations[Ant].spectro_ch0[t][f];
                double p1 = Stations[Ant].spectro_ch1[t][f];

                if (p0 != 0.0) {
                    soma_CH0[grupo] += p0;
                    quantidade_CH0[grupo]++;
                }

                if (p1 != 0.0) {
                    soma_CH1[grupo] += p1;
                    quantidade_CH1[grupo]++;
                }
            }
        }
    }

    ofstream saida_grupos("Media_Potencia_Grupos.txt");

    saida_grupos << fixed << setprecision(8);
    saida_grupos << "Grupo\tAntenas\tMedia_CH0\tMedia_CH1\n";

    for (const auto& grupo : grupos) {

        int g = grupo.first;

        double media_CH0 = 0.0;
        double media_CH1 = 0.0;

        if (quantidade_CH0[g] > 0)
            media_CH0 = soma_CH0[g] / quantidade_CH0[g];

        if (quantidade_CH1[g] > 0)
            media_CH1 = soma_CH1[g] / quantidade_CH1[g];

        saida_grupos << g << "\t"
                     << grupo.second << "\t"
                     << media_CH0 << "\t"
                     << media_CH1 << "\n";
    }

    saida_grupos.close();


    // ============================================================
    // 3. Salvar posições das antenas
    // ============================================================

    ofstream saida_posicoes("Posicoes_Antenas.txt");

    saida_posicoes << fixed << setprecision(8);
    saida_posicoes << "ID\tNorthing\tEasting\tinGrid\n";

    for (int Ant = 0; Ant < Stations.size(); Ant++) {

        saida_posicoes << Stations[Ant].ID << "\t"
                       << Stations[Ant].northing << "\t"
                       << Stations[Ant].easting << "\t"
                       << Stations[Ant].ingrid << "\n";
    }

    saida_posicoes.close();


    // ============================================================
    // 4. Estatísticas individuais por antena
    // ============================================================

    ofstream saida_individual("Estatisticas_Individuais.txt");

    saida_individual << fixed << setprecision(8);
    saida_individual << "ID\tinGrid\tMedia_CH0\tDesvio_CH0\t"
                     << "Media_CH1\tDesvio_CH1\t"
                     << "N_CH0\tN_CH1\n";

    for (int Ant = 0; Ant < Stations.size(); Ant++) {

        double soma0 = 0.0;
        double soma1 = 0.0;

        double soma_quadrados0 = 0.0;
        double soma_quadrados1 = 0.0;

        int quantidade0 = 0;
        int quantidade1 = 0;

        for (int t = 0; t < 24; t++) {
            for (int f = 0; f < 50; f++) {
                double p0 = Stations[Ant].spectro_ch0[t][f];
                double p1 = Stations[Ant].spectro_ch1[t][f];

                // CH0
                if (p0 != 0.0) {
                    soma0 += p0;
                    soma_quadrados0 += p0 * p0;
                    quantidade0++;
                }

                // CH1
                if (p1 != 0.0) {
                    soma1 += p1;
                    soma_quadrados1 += p1 * p1;
                    quantidade1++;
                }
            }
        }

        // Estatísticas do CH0
        double media0 = 0.0;
        double desvio0 = 0.0;
        if (quantidade0 > 0) {
            media0 = soma0 / quantidade0;
            double variancia0 =
                soma_quadrados0 / quantidade0 - media0 * media0;
            desvio0 = sqrt(max(0.0, variancia0));
        }

        // Estatísticas do CH1
        double media1 = 0.0;
        double desvio1 = 0.0;

        if (quantidade1 > 0) {
            media1 = soma1 / quantidade1;
            double variancia1 =
                soma_quadrados1 / quantidade1 - media1 * media1;
            desvio1 = sqrt(max(0.0, variancia1));
        }

        // Salvar resultados individuais
        saida_individual << Stations[Ant].ID << "\t"
                         << Stations[Ant].ingrid << "\t";
        if (quantidade0 > 0)
            saida_individual << media0 << "\t" << desvio0 << "\t";
        else
            saida_individual << "NA\tNA\t";
        if (quantidade1 > 0)
            saida_individual << media1 << "\t" << desvio1 << "\t";
        else
            saida_individual << "NA\tNA\t";
        saida_individual << quantidade0 << "\t"
                         << quantidade1 << "\n";
    }
    // Fecha somente depois de terminar o for
    saida_individual.close();

    // ============================================================
    // 5. Estatísticas por configuração de malha
    // ============================================================

    map<int, vector<double>> medias_CH0;
    map<int, vector<double>> medias_CH1;

    for (int Ant = 0; Ant < Stations.size(); Ant++) {

        double soma0 = 0.0;
        double soma1 = 0.0;
        int quantidade0 = 0;
        int quantidade1 = 0;

        for (int t = 0; t < 24; t++) {
            for (int f = 0; f < 50; f++) {
                double p0 = Stations[Ant].spectro_ch0[t][f];
                double p1 = Stations[Ant].spectro_ch1[t][f];

                if (p0 != 0.0) {
                    soma0 += p0;
                    quantidade0++;
                }
                if (p1 != 0.0) {
                    soma1 += p1;
                    quantidade1++;
                }
            }
        }

        int grupo = Stations[Ant].ingrid;
        if (quantidade0 > 0)
            medias_CH0[grupo].push_back(soma0 / quantidade0);
        if (quantidade1 > 0)
            medias_CH1[grupo].push_back(soma1 / quantidade1);
    }

    // Salvar comparação dos grupos
    ofstream saida_comparacao("Comparacao_Grupos.txt");
    saida_comparacao << fixed << setprecision(8);
    saida_comparacao << "inGrid\tN_CH0\tMedia_CH0\tDesvio_CH0\t"
                     << "N_CH1\tMedia_CH1\tDesvio_CH1\n";

    for (const auto& grupo : grupos) {
    	int g = grupo.first;
        double media0 = 0.0;
        double desvio0 = 0.0;
        double media1 = 0.0;
        double desvio1 = 0.0;

        // CH0
        if (!medias_CH0[g].empty()) {
            for (double valor : medias_CH0[g])
                media0 += valor;
            media0 /= medias_CH0[g].size();
            for (double valor : medias_CH0[g])
                desvio0 += pow(valor - media0, 2);
            desvio0 = sqrt(desvio0 / medias_CH0[g].size());
        }

        // CH1
        if (!medias_CH1[g].empty()) {
            for (double valor : medias_CH1[g])
                media1 += valor;
            media1 /= medias_CH1[g].size();
            for (double valor : medias_CH1[g])
                desvio1 += pow(valor - media1, 2);
            desvio1 = sqrt(desvio1 / medias_CH1[g].size());
        }
        saida_comparacao << g << "\t"
                         << medias_CH0[g].size() << "\t"
                         << media0 << "\t"
                         << desvio0 << "\t"
                         << medias_CH1[g].size() << "\t"
                         << media1 << "\t"
                         << desvio1 << "\n";
    }
    saida_comparacao.close();

    // ============================================================
    // 6. Identificação de antenas atípicas
    // ============================================================

    struct DadosAntena {
        int ID;
        int inGrid;
        double media0;
        double desvio0;
        double media1;
        double desvio1;
    };

    vector<DadosAntena> antenas;
    ifstream entrada_individual("Estatisticas_Individuais.txt");
    if (!entrada_individual.is_open()) {
        cerr << "Erro ao abrir Estatisticas_Individuais.txt" << endl;
        return;
    }

    string linha;
    // Ignorar cabeçalho
    getline(entrada_individual, linha);
    while (getline(entrada_individual, linha)) {

        stringstream ss(linha);
        string campo;
        vector<string> campos;

        while (ss >> campo)
            campos.push_back(campo);
        if (campos.size() != 8)
            continue;

        // Ignorar antenas sem dados válidos em algum canal
        if (campos[2] == "NA" || campos[3] == "NA" ||
            campos[4] == "NA" || campos[5] == "NA")
            continue;
        int N0 = stoi(campos[6]);
        int N1 = stoi(campos[7]);

        if (N0 == 0 || N1 == 0)
            continue;
        DadosAntena dados;
        dados.ID = stoi(campos[0]);
        dados.inGrid = stoi(campos[1]);
        dados.media0 = stod(campos[2]);
        dados.desvio0 = stod(campos[3]);
        dados.media1 = stod(campos[4]);
        dados.desvio1 = stod(campos[5]);
        antenas.push_back(dados);
    }
    entrada_individual.close();

    // Separar os valores por configuração de malha
    map<int, vector<double>> grupos_media0;
    map<int, vector<double>> grupos_desvio0;
    map<int, vector<double>> grupos_media1;
    map<int, vector<double>> grupos_desvio1;

    for (const auto& Ant : antenas) {
        grupos_media0[Ant.inGrid].push_back(Ant.media0);
        grupos_desvio0[Ant.inGrid].push_back(Ant.desvio0);

        grupos_media1[Ant.inGrid].push_back(Ant.media1);
        grupos_desvio1[Ant.inGrid].push_back(Ant.desvio1);
    }

    // Calcular média e desvio padrão de cada grupo
    struct EstatisticasGrupo {
        double media;
        double desvio;
    };

    map<int, EstatisticasGrupo> estatisticas_media0;
    map<int, EstatisticasGrupo> estatisticas_desvio0;
    map<int, EstatisticasGrupo> estatisticas_media1;
    map<int, EstatisticasGrupo> estatisticas_desvio1;

    auto calcularEstatisticas = [](const vector<double>& valores) {
        EstatisticasGrupo resultado{0.0, 0.0};
        if (valores.empty())
            return resultado;
        for (double valor : valores)
            resultado.media += valor;
        resultado.media /= valores.size();
        for (double valor : valores)
            resultado.desvio += pow(valor - resultado.media, 2);
        resultado.desvio =
            sqrt(resultado.desvio / valores.size());
        return resultado;
    };

    for (const auto& grupo : grupos_media0) {
        int g = grupo.first;
        estatisticas_media0[g] =
            calcularEstatisticas(grupos_media0[g]);
        estatisticas_desvio0[g] =
            calcularEstatisticas(grupos_desvio0[g]);
        estatisticas_media1[g] =
            calcularEstatisticas(grupos_media1[g]);
        estatisticas_desvio1[g] =
            calcularEstatisticas(grupos_desvio1[g]);
    }

    // Calcular escores-z e classificar antenas
    ofstream saida_atipicas("Antenas_Atipicas.txt");
    saida_atipicas << fixed << setprecision(8);
    saida_atipicas
        << "ID\tinGrid\tN_Grupo\t"
        << "Media_CH0\tZ_Media_CH0\t"
        << "Desvio_CH0\tZ_Desvio_CH0\t"
        << "Media_CH1\tZ_Media_CH1\t"
        << "Desvio_CH1\tZ_Desvio_CH1\t"
        << "Classificacao\n";


    for (const auto& Ant : antenas) {
        int grupo = Ant.inGrid;
        int N = grupos_media0[grupo].size();
        double z_media0 = 0.0;
        double z_desvio0 = 0.0;
        double z_media1 = 0.0;
        double z_desvio1 = 0.0;
        bool valido_media0 =
            estatisticas_media0[grupo].desvio > 0.0;
        bool valido_desvio0 =
            estatisticas_desvio0[grupo].desvio > 0.0;
        bool valido_media1 =
            estatisticas_media1[grupo].desvio > 0.0;
        bool valido_desvio1 =
            estatisticas_desvio1[grupo].desvio > 0.0;

        if (valido_media0)
            z_media0 =
                (Ant.media0 - estatisticas_media0[grupo].media) /
                estatisticas_media0[grupo].desvio;
        if (valido_desvio0)
            z_desvio0 =
                (Ant.desvio0 - estatisticas_desvio0[grupo].media) /
                estatisticas_desvio0[grupo].desvio;
        if (valido_media1)
            z_media1 =
                (Ant.media1 - estatisticas_media1[grupo].media) /
                estatisticas_media1[grupo].desvio;
        if (valido_desvio1)
            z_desvio1 =
                (Ant.desvio1 - estatisticas_desvio1[grupo].media) /
                estatisticas_desvio1[grupo].desvio;

        double maior_z = 0.0;
        if (valido_media0)
            maior_z = max(maior_z, abs(z_media0));
        if (valido_desvio0)
            maior_z = max(maior_z, abs(z_desvio0));
        if (valido_media1)
            maior_z = max(maior_z, abs(z_media1));
        if (valido_desvio1)
            maior_z = max(maior_z, abs(z_desvio1));

        string classificacao;
        if (N < 10)
            classificacao = "AMOSTRA_PEQUENA";
        else if (maior_z >= 3.0)
            classificacao = "ATIPICA";
        else if (maior_z >= 2.0)
            classificacao = "ATENCAO";
        else
            classificacao = "NORMAL";

        saida_atipicas
            << Ant.ID << "\t"
            << grupo << "\t"
            << N << "\t"
            << Ant.media0 << "\t";

        if (valido_media0)
            saida_atipicas << z_media0;
        else
            saida_atipicas << "NA";
        saida_atipicas << "\t" << Ant.desvio0 << "\t";

        if (valido_desvio0)
            saida_atipicas << z_desvio0;
        else
            saida_atipicas << "NA";
        saida_atipicas << "\t" << Ant.media1 << "\t";

        if (valido_media1)
            saida_atipicas << z_media1;
        else
            saida_atipicas << "NA";
        saida_atipicas << "\t" << Ant.desvio1 << "\t";

        if (valido_desvio1)
            saida_atipicas << z_desvio1;
        else
            saida_atipicas << "NA";
        saida_atipicas << "\t" << classificacao << "\n";
    }
    saida_atipicas.close();

    // ============================================================
    // 7. Comparação entre os canais CH0 e CH1
    // ============================================================

    ofstream saida_canais("Comparacao_Canais.txt");
    saida_canais << fixed << setprecision(8);
    saida_canais << "Antena\tMedia_CH0\tMedia_CH1\t"
                 << "Diferenca\tDiferenca_Relativa(%)\n";

    // Utiliza o vetor antenas, que contém somente antenas
    // com dados válidos nos dois canais.
    for (const auto& Ant : antenas) {
        double diferenca = Ant.media1 - Ant.media0;
        double diferenca_relativa = 0.0;

        if (Ant.media0 != 0.0)
            diferenca_relativa =
                (diferenca / Ant.media0) * 100.0;

        saida_canais << Ant.ID << "\t"
                     << Ant.media0 << "\t"
                     << Ant.media1 << "\t"
                     << diferenca << "\t"
                     << diferenca_relativa << "\n";
    }
    saida_canais.close();

} // fim da função Posicoes

struct Posicao {
    double northing;
    double easting;
    int inGrid;
};

struct EstatisticaAntena {
    double media0;
    double media1;
    bool temCH0;
    bool temCH1;
};

struct Celula {
    int quantidade = 0;

    double soma0 = 0.0;
    double somaQuadrados0 = 0.0;
    int n0 = 0;

    double soma1 = 0.0;
    double somaQuadrados1 = 0.0;
    int n1 = 0;

    int atipicas = 0;
    int atencao = 0;

    map<int, int> grupos;
};

void AnaliseEspacial() {

    const double tamanhoCelula = 2000.0;
    // 1. Ler as posições das antenas
    map<int, Posicao> posicoes;
    ifstream arquivoPosicoes("Posicoes_Antenas.txt");
    if (!arquivoPosicoes.is_open()) {
        cerr << "Erro ao abrir Posicoes_Antenas.txt\n";
        return;
    }

    string linha;
    getline(arquivoPosicoes, linha); // Ignorar cabeçalho
    int id, grupo;
    double northing, easting;
    while (arquivoPosicoes >> id >> northing >> easting >> grupo) {
        posicoes[id] = {northing, easting, grupo};
    }
    arquivoPosicoes.close();

    // 2. Ler as estatísticas individuais
    map<int, EstatisticaAntena> estatisticas;
    ifstream arquivoEstatisticas("Estatisticas_Individuais.txt");
    if (!arquivoEstatisticas.is_open()) {
        cerr << "Erro ao abrir Estatisticas_Individuais.txt\n";
        return;
    }

    getline(arquivoEstatisticas, linha);
    string campo0, campo1, campo;
    while (getline(arquivoEstatisticas, linha)) {

        stringstream ss(linha);
        int idAntena, inGrid;
        ss >> idAntena >> inGrid >> campo0;
        EstatisticaAntena dados;
        dados.temCH0 = (campo0 != "NA");
        if (dados.temCH0)
            dados.media0 = stod(campo0);
        ss >> campo;
        ss >> campo1;
        dados.temCH1 = (campo1 != "NA");
        if (dados.temCH1)
            dados.media1 = stod(campo1);
        estatisticas[idAntena] = dados;
    }
    arquivoEstatisticas.close();

    // 3. Ler a classificação das antenas
    map<int, string> classificacoes;
    ifstream arquivoAtipicas("Antenas_Atipicas.txt");
    if (!arquivoAtipicas.is_open()) {
        cerr << "Erro ao abrir Antenas_Atipicas.txt\n";
        return;
    }

    getline(arquivoAtipicas, linha);
    while (getline(arquivoAtipicas, linha)) {

        stringstream ss(linha);
        int idAntena, inGrid, nGrupo;
        string classificacao;
        ss >> idAntena >> inGrid >> nGrupo;

        // As dez colunas intermediárias
        for (int i = 0; i < 8; i++)
            ss >> campo;
        ss >> classificacao;
        classificacoes[idAntena] = classificacao;
    }
    arquivoAtipicas.close();

    // 4. Agrupar antenas nas células espaciais
    map<pair<long long, long long>, Celula> celulas;

    for (const auto& elemento : posicoes) {
        int idAntena = elemento.first;
        const Posicao& pos = elemento.second;

        // Identificar a célula espacial
        long long eastingCelula = floor(pos.easting / tamanhoCelula) * tamanhoCelula;
        long long northingCelula = floor(pos.northing / tamanhoCelula) * tamanhoCelula;
        auto chave = make_pair(eastingCelula, northingCelula);
        Celula& celula = celulas[chave];
        celula.quantidade++;

        // Contabilizar configuração da malha
        celula.grupos[pos.inGrid]++;

        // Estatísticas individuais
        auto it = estatisticas.find(idAntena);

        if (it != estatisticas.end()) {
            const EstatisticaAntena& dados = it->second;
            if (dados.temCH0) {
                celula.soma0 += dados.media0;
                celula.somaQuadrados0 += dados.media0 * dados.media0;
                celula.n0++;
            }
            if (dados.temCH1) {
                celula.soma1 += dados.media1;
                celula.somaQuadrados1 += dados.media1 * dados.media1;
                celula.n1++;
            }
        }

        // Contabilizar classificações
        auto ic = classificacoes.find(idAntena);
        if (ic != classificacoes.end()) {
            if (ic->second == "ATIPICA")
                celula.atipicas++;
            else if (ic->second == "ATENCAO")
                celula.atencao++;
        }
    }

    // 5. Salvar resultados
    ofstream saida("Padroes_Espaciais_2km.txt");
    if (!saida.is_open()) {
        cerr << "Erro ao criar Padroes_Espaciais_2km.txt\n";
        return;
    }

    saida << fixed << setprecision(8);
   	saida << "Easting_Inicial\tNorthing_Inicial\t"
      	  << "Easting_Centro\tNorthing_Centro\t"
	  	  << "N_Antenas\tArea_km2\tDensidade_ant_km2\t"
		  << "N_CH0\tMedia_CH0\tDesvio_CH0\t"
		  << "N_CH1\tMedia_CH1\tDesvio_CH1\t"
		  << "N_Atipicas\tN_Atencao\t"
		  << "Grid_1\tGrid_2\tGrid_3\t"
		  << "Grid_12\tGrid_23\tGrid_123\n";

	double areaKm2 = pow(tamanhoCelula / 1000.0, 2);
    for (const auto& elemento : celulas) {

        long long x = elemento.first.first;
        long long y = elemento.first.second;
        const Celula& c = elemento.second;
        double media0 = 0.0;
        double desvio0 = 0.0;
        double media1 = 0.0;
        double desvio1 = 0.0;
		
		double densidade = c.quantidade / areaKm2;

        if (c.n0 > 0) {
            media0 = c.soma0 / c.n0;
            double variancia0 =
                c.somaQuadrados0 / c.n0 - media0 * media0;
            desvio0 = sqrt(max(0.0, variancia0));
        }

        if (c.n1 > 0) {
            media1 = c.soma1 / c.n1;
            double variancia1 =
                c.somaQuadrados1 / c.n1 - media1 * media1;
            desvio1 = sqrt(max(0.0, variancia1));
        }
        saida << x << "\t"
			<< y << "\t"
			<< x + tamanhoCelula / 2.0 << "\t"
			<< y + tamanhoCelula / 2.0 << "\t"
			<< c.quantidade << "\t"
			<< areaKm2 << "\t"
			<< densidade << "\t"
			<< c.n0 << "\t"
			<< media0 << "\t"
			<< desvio0 << "\t"
			<< c.n1 << "\t"
			<< media1 << "\t"
			<< desvio1 << "\t"
			<< c.atipicas << "\t"
			<< c.atencao << "\t"
			<< ValorGrupo(c.grupos, 1) << "\t"
			<< ValorGrupo(c.grupos, 2) << "\t"
			<< ValorGrupo(c.grupos, 3) << "\t"
			<< ValorGrupo(c.grupos, 12) << "\t"
			<< ValorGrupo(c.grupos, 23) << "\t"
			<< ValorGrupo(c.grupos, 123) << "\n";
    }

    saida.close();
    cout << "Analise espacial concluida!\n";
    cout << "Celulas ocupadas: " << celulas.size() << "\n";
}

void GerarEspectrograma(vector<Antena_info>& Stations)
{
    const int NT = 24;
    const int NF = 51;

    double soma_CH0[NT][NF] = {};
    double soma_CH1[NT][NF] = {};

    int contador_CH0[NT][NF] = {};
    int contador_CH1[NT][NF] = {};

    // Percorre todas as antenas
    for (int Ant = 0; Ant < Stations.size(); Ant++)
    {
        // Descarta antenas que não pertencem a uma grade
        if (Stations[Ant].ingrid == 0)
            continue;

        // Percorre os tempos e as frequências
        for (int t = 0; t < NT; t++)
        {
            for (int f = 0; f < NF; f++)
            {
                double p0 = Stations[Ant].spectro_ch0[t][f];
                double p1 = Stations[Ant].spectro_ch1[t][f];

                // CH0
                if (p0 != 0.0)
                {
                    soma_CH0[t][f] += p0;
                    contador_CH0[t][f]++;
                }

                // CH1
                if (p1 != 0.0)
                {
                    soma_CH1[t][f] += p1;
                    contador_CH1[t][f]++;
                }
            }
        }
    }

    // Arquivo de saída
    ofstream saida("Espectrograma_Medio.txt");

    if (!saida.is_open())
    {
        cerr << "Erro ao criar Espectrograma_Medio.txt\n";
        return;
    }

    saida << "LST Frequencia Media_CH0 Media_CH1 "
          << "N_CH0 N_CH1\n";

    saida << fixed << setprecision(6);

    // Escreve os resultados
    for (int t = 0; t < NT; t++)
    {
        for (int f = 0; f < NF; f++)
        {
            double media0 = 0.0;
            double media1 = 0.0;

            if (contador_CH0[t][f] > 0)
                media0 = soma_CH0[t][f] / contador_CH0[t][f];

            if (contador_CH1[t][f] > 0)
                media1 = soma_CH1[t][f] / contador_CH1[t][f];

            // Conversão dos índices para os valores físicos
            double LST = t + 0.5;
            double frequencia = f + 30.5;

            saida << LST << " "
                  << frequencia << " "
                  << media0 << " "
                  << media1 << " "
                  << contador_CH0[t][f] << " "
                  << contador_CH1[t][f] << "\n";
        }
    }

    saida.close();

    cout << "Arquivo Espectrograma_Medio.txt gerado!\n";
}


int main(){

	ifstream data_positions("Positions.txt");

	if (!data_positions.is_open()) {
        cerr << "Erro ao abrir Positions.txt\n";
        return 1;
    }

	vector<Antena_info> Stations;
	Antena_info Stations_Aux;

	string cabecalho;
	getline(data_positions, cabecalho);

	while (data_positions >> Stations_Aux.ingrid
                     >> Stations_Aux.ID
                     >> Stations_Aux.northing
                     >> Stations_Aux.easting) {

		if (Stations_Aux.ingrid == 0) {
        continue;
    	}

		Stations_Aux.ID_arquivo = Stations_Aux.ID + 30000;

    	Stations.push_back(Stations_Aux);
	}

	data_positions.close();

	for (int Ant = 0; Ant < Stations.size(); Ant++) {
    	for (int t = 0; t < 24; t++) {
        	for (int f = 0; f < 50; f++) {
            Stations[Ant].spectro_ch0[t][f] = 0.0;
            Stations[Ant].spectro_ch1[t][f] = 0.0;
        	}
    	}
	}

	// lendo os espectros de cada antena para o canal 0
	for (int Ant = 0; Ant < Stations.size(); Ant++) {
		string Name_Spectro = "Files_Spectrograma/Antenna_" + to_string(Stations[Ant].ID_arquivo) + "_CH0.txt";
		
		ifstream data_Spectro(Name_Spectro);

	 	// 	if (!data_Spectro.is_open()) {
    	//	cerr << "Arquivo CH0 ausente para antena "
        //	<< Stations[Ant].ID
        //	<< " (arquivo esperado: " << Name_Spectro << ")\n";
    	//	continue;
		// } 
			
		double tempo, freq, power;
		while (data_Spectro >> tempo >> freq >> power) {
			int t = static_cast<int>(round(tempo - 0.5));
			int f = static_cast<int>(round(freq - 30.5));	
			if (t >= 0 && t < 24 && f >= 0 && f < 50) {
    			Stations[Ant].spectro_ch0[t][f] = power;
			}
		}

    	data_Spectro.close();	
	}


	// lendo os espectros de cada antena para o canal 1
	for (int Ant = 0; Ant < Stations.size(); Ant++) {
		string Name_Spectro = "Files_Spectrograma/Antenna_" + to_string(Stations[Ant].ID_arquivo) + "_CH1.txt";
		ifstream data_Spectro(Name_Spectro);

		// 	if (!data_Spectro.is_open()) {
    	//	cerr << "Arquivo CH1 ausente para antena "
         //	<< Stations[Ant].ID
         //	<< " (arquivo esperado: " << Name_Spectro << ")\n";
    	//	continue;
		//}

		double tempo, freq, power;
		while (data_Spectro >> tempo >> freq >> power) {
			int t = static_cast<int>(round(tempo - 0.5));
			int f = static_cast<int>(round(freq - 30.5));
			if (t >= 0 && t < 24 && f >= 0 && f < 50) {
    			Stations[Ant].spectro_ch1[t][f] = power;
				}
		}
    	data_Spectro.close();
	}
	

	cout << "Total de antenas: " << Stations.size() << endl;
	cout << "Analisando espectros...\n";

	//AnaliseEspectro(Stations);
	//Posicoes(Stations);
	GerarEspectrograma(Stations);
	return 0;
}



