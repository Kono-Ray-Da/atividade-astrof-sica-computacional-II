#include <fstream>
#include <iomanip>
#include <iostream>
#include <vector>
#include <cmath>
#include <sstream>
#include <limits>

using namespace std;

const double Rad2Deg = 180./M_PI;
const double Deg2Rad = M_PI/180.;

struct CoordenadasGalaticas {
    double l;
    double b;
};

double RadiansToDegree(double ValueRadians){
    return ValueRadians*Rad2Deg;
}

double ComputeAngularDistance(double lpoint1, double lpoint2, double bpoint1, double bpoint2){
    double cosTheta = sin (bpoint1) * sin(bpoint2) + cos(bpoint1) * cos(bpoint2) * cos(lpoint1 - lpoint2);
    double Distance = acos(cosTheta);
    // Evita erros numericos no acos
    if (cosTheta > 1.0) cosTheta = 1.0;
    if (cosTheta < -1.0) cosTheta = -1.0;
    return RadiansToDegree(Distance);
}

double DegreeToRadians(double ValueDegree){
    return ValueDegree*Deg2Rad;
}


CoordenadasGalaticas CoordenadaEquatorialGalatica(double ra_deg, double dec_deg) {

    //passar as coordenadas equatoriais para radianos
    double ra = ra_deg*Deg2Rad;
    double dec = dec_deg*Deg2Rad;

    //treansformação de coordenadas equatoriais para cartesianas
    double x = cos(dec)*cos(ra);;
    double y = cos(dec)*sin(ra);
    double z = sin(dec);

    //aplicando matriz de rotação J2000.0
    double X = -0.05487556 * x + 0.49410943 * y - 0.86766615 * z;
    double Y = -0.87343709 * x - 0.44482963 * y - 0.19807637 * z;
    double Z = -0.48383502 * x + 0.74698224 * y + 0.45598378 * z;

    //Convertendo de coordenadas cartesianas para coordenadas galáticas
    double b_rad = asin(Z);
    double l_rad = atan2(Y, X);

    //passando de radianos para graus
    double b = b_rad * Rad2Deg;
    double l = l_rad * Rad2Deg;

    //ajustando o valor de l para o intervalo de 0 a 360
    if (l < 0) {
        l += 360.0;
    }

    return CoordenadasGalaticas{l, b};
}


void converterCoordenadas() {

    //lendo o arquivo de eventos e devolvendo o arquivo com as coordenadas galaticas
    ifstream entrada("Eventos.txt");
    ofstream saida("eventos_galaticos.txt");

    //cout << "arquivo de saida aberto" << endl;

    if (!entrada){
        cerr << "erro ao abrir eventos.txt" << endl;
    }

    if (!saida){
        cerr << "erro ao abrir eventos_galaticos.txt" << endl;
    }

    //cabeçalho do arquivo de saída
    saida << "# AugId l b Ecor UTC Theta Phi T5 FTR" << endl;

    long long AugId;
    double Dec, Ra, Ecor, Theta, Phi, UTC;
    int t5, ftr;
    double l, b;

    string linha;

    while (getline(entrada, linha)) {

            //cout << "linha lida: [" << linha << "]" << augId << endl;
        
            stringstream ss(linha);

            if (ss >> AugId >> Dec >> Ra >> Ecor >> UTC >> Theta >> Phi >> t5 >> ftr) {
                //cout << "LEITURA DOS 9 VALORES OK!" << endl;
                //cout << "AugId = " << AugId << endl;
                //cout << "Dec   = " << Dec << endl;
                //cout << "RA    = " << Ra << endl;
            
                CoordenadasGalaticas galaticas = CoordenadaEquatorialGalatica(Ra, Dec);

                //cout << "l = " << galaticas.l << endl;
                //cout << "b = " << galaticas.b << endl;
                
                //cout << "escrevendo no arquivo de saida..." << endl;
                saida << AugId << " "<< galaticas.l << " "
                      << galaticas.b << " "
                      << Ecor << " "
                      << UTC << " "
                      << Theta  << " "
                      << Phi << " "
                      << t5 << " "
                      << ftr
                      << endl;
                
                    //cout << "escrevi um evento no arquivo" << endl;

            }else{
             //cout << "ERRO AO CONVERTER ESTA LINHA!" << endl;
            }
    }

            entrada.close();
            saida.close();
            cout << "conversão feita de (ra,dec) para (l,b) " << endl;

}

struct EventosGalaticos {
    long long  AugId;
    double l;
    double b;
    double Ecor;
    double UTC;
    double Theta;
    double Phi;
    int T5;
    int FTR;
};

struct FontesAstrofisicas {
    double L;
    double B;
    double Distancia;
    double Wtotal;
};

double funcaopeso (double sigma, double ComputeAngularDistance){
    double k = 1./pow(sigma,2);
    return exp(k*(cos(ComputeAngularDistance)-1.));
};

void Energias (vector<EventosGalaticos> eventos){ //troca o nome plss

    ofstream saida10("Eventos_com_Energia_Maior_Que_10.txt");
    ofstream saida20("Eventos_com_Energia_Maior_Que_20.txt");
    ofstream saida40("Eventos_com_Energia_Maior_Que_40.txt");
    ofstream saida60("Eventos_com_Energia_Maior_Que_60.txt");

    saida10 << "# AugId Ecor l b" << endl;
    saida20 << "# AugId Ecor l b" << endl;
    saida40 << "# AugId Ecor l b" << endl;
    saida60 << "# AugId Ecor l b" << endl;

    //cout << "ENTREI NA FUNCAO ENERGIAS" << endl;
    //cout << "numero de eventos: " << eventos.size() << endl;

    for (int i=0; i<eventos.size(); i++){

        if(eventos[i].Ecor >=10 && eventos[i].Ecor<20 ){
            saida10 << "AugId: " << eventos[i].AugId << "\tl: " << eventos[i].l << "\tb: " << eventos[i].b << "\tEcor: " << eventos[i].Ecor << endl;
        }

        if(eventos[i].Ecor >= 20 && eventos[i].Ecor < 40){
            saida20 << "AugId: " << eventos[i].AugId << "\tl: " << eventos[i].l << "\tb: " << eventos[i].b << "\tEcor: " << eventos[i].Ecor << endl;
        }

        if(eventos[i].Ecor >= 40 && eventos[i].Ecor < 60){
            saida40 << "AugId: " << eventos[i].AugId << "\tl: " << eventos[i].l << "\tb: " << eventos[i].b << "\tEcor: " << eventos[i].Ecor << endl;
        }

        if(eventos[i].Ecor >= 60){
            saida60 << "AugId: " << eventos[i].AugId << "\tl: " << eventos[i].l << "\tb: " << eventos[i].b << "\tEcor: " << eventos[i].Ecor << endl;
        }
    }
    saida10.close();
    saida20.close();
    saida40.close();
    saida60.close();
}

void FA (const vector<FontesAstrofisicas> fontes, const vector<EventosGalaticos> eventos){

    // janela angular
    // distancia media

    int total = fontes.size();
    double numStarbursts [fontes.size()][3]={0}; 

    for (int janelAng=5; janelAng<20; janelAng+=5){

        vector<double> score(fontes.size(), 0.0);

        for (int ifontes=0; ifontes<fontes.size(); ifontes++){

            for (int iEventos=0; iEventos<eventos.size(); iEventos++){

                double eventol = DegreeToRadians(eventos[iEventos].l);
                double eventob = DegreeToRadians(eventos[iEventos].b);

                double fontel = DegreeToRadians(fontes[ifontes].L);
                double fonteb = DegreeToRadians(fontes[ifontes].B);

                // calculo da distancia angular entre dois pontos na esfera celeste
                double angulo = ComputeAngularDistance(fontel, eventob, fontel, eventol);

                 double peso = funcaopeso(janelAng, angulo);

                //tem q ter o -1 pq a primeira posição tem indice 0
                if (angulo <= janelAng) {
                    //cout << "chegou aqui" << endl;
                    //cout << "fonte: " << IndexFontes+1 << " janela angular: " << janelaAngular << endl;
                    numStarbursts[ifontes][(janelAng/5)-1] += peso;
                    score[ifontes] += peso;  
                }


            } //fim do for dos eventos

        } //fim do for das fontes

        cout << "Terminou calculo da janela " << janelAng << endl;
    

        vector<int> indice(fontes.size());

        // Guarda a identificação original de cada fonte
        for (int i = 0; i < fontes.size(); i++) {
            indice[i] = i;
        }

        //cout << "Terminou calculo da janela " << janelaAngular << endl;
        //cout << "Comecando ordenacao..." << endl;

        // Procura o maior score e coloca no início
        for (int i = 0; i < fontes.size() - 1; i++) {
            int maior = i;

            for (int j = i + 1; j < fontes.size(); j++) {

                if (score[j] > score[maior]) {
                    maior = j;
                }
            }

            // troca os scores
            double auxScore = score[i];
            score[i] = score[maior];
            score[maior] = auxScore;

            // troca também os índices das fontes
            int auxIndice = indice[i];
            indice[i] = indice[maior];
            indice[maior] = auxIndice;
        }

        string Nome = "resultado_"+to_string(janelAng)+".txt";

        ofstream saida(Nome.c_str());
        saida << "Ranking\tl\tb\tS_j\tIdentificacao_da_fonte\n";
        //cout << "Numero de fontes: " << fontes.size() << endl;

        for (int i = 0; i < 10 && i < fontes.size(); i++) {

            int ponto = indice[i];

            saida << i + 1 << "\t"
                << fontes[ponto].L << "\t"
                << fontes[ponto].B << "\t"
                << score[i] << "\t"
                << ponto + 1
                << "\n";
        }

        saida.close();
        
        cout << "Resultados escritos no arquivo " << Nome << endl;
    
    
    
    
    
    
    
    
    } //fim da janela angular






}




int main() {  
    vector<FontesAstrofisicas> fontes;
     ifstream arquivo2("2MASS.txt");
     //cout << "arquivo 2mass aberto" << endl;
    if (!arquivo2){
        cerr << "erro ao abrir arquivo 2MASS" << endl;
        return 1;
    }
    while (!arquivo2.eof()) {
        FontesAstrofisicas fontesTemp;
        arquivo2 >> fontesTemp.L
                 >> fontesTemp.B
                 >> fontesTemp.Distancia
                 >> fontesTemp.Wtotal;

        fontes.push_back(fontesTemp);
    }
    arquivo2.close();

    cout << "numero de fontes lidoa: " << fontes.size() << endl;


    vector<EventosGalaticos> eventos;
    ifstream arquivo1("eventos_galaticos.txt");
    //cout << "arquivo eventos_galaticos.txt aberto" << endl;

    if (!arquivo1){
        cerr << "erro ao abrir arquivo eventos-galaticos"<< endl;
        return 1;
    }

    arquivo1.ignore(1000, '\n');
    //cout << "estado antes da leitura: " << arquivo1.good() << endl;

    EventosGalaticos eventosTemp;

    while (arquivo1 >> eventosTemp.AugId
                >> eventosTemp.l
                >> eventosTemp.b
                >> eventosTemp.Ecor
                >> eventosTemp.UTC
                >> eventosTemp.Theta
                >> eventosTemp.Phi
                >> eventosTemp.T5
                >> eventosTemp.FTR) {

                //cout << "augId: " << eventosTemp.AugId << ", l: " << eventosTemp.l << ", b: " << eventosTemp.b << ", Ecor: " << eventosTemp.Ecor << endl;
                //cout << "proximo caractere: " << arquivo1.peek() << endl;
        eventos.push_back(eventosTemp);
    
    }
        

    arquivo1.close();

    cout << "numero de eventos lidos: " << eventos.size() << endl;


    //Energias(eventos);
    FA(fontes, eventos);

}