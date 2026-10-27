#include <fstream>
#include <iomanip>
#include <iostream>
#include <vector>
#include <cmath>
#include <sstream>

using namespace std;

const double Rad2Deg = 180./M_PI;
const double Deg2Rad = M_PI/180.;

struct CoordenadasGalaticas {
    double l;
    double b;
};

struct fontes {
    double fontesl;
    double fontesb;
    double distancia;
    double utc;
    double score;
};

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




int main() {  
    vector<fontes> pontos;
     ifstream arquivo2("2MASS.txt");
    if (!arquivo2){
        cerr << "erro ao abrir arquivo 2MASS" << endl;
        return 1;
    }
    while (!arquivo2.eof()) {
        fontes fontesTemp;
        arquivo2 >> fontesTemp.fontesl
                 >> fontesTemp.fontesb
                 >> fontesTemp.distancia
                 >> fontesTemp.utc;

        pontos.push_back(fontesTemp);
    }
    arquivo2.close();

    //converterCoordenadas();

    vector<EventosGalaticos> eventos;
    ifstream arquivo1("eventos_galaticos.txt");
    //cout << "arquivo eventos_galaticos.txt aberto" << endl;
    if (!arquivo1){
        cerr << "erro ao abrir arquivo eventos-galaticos"<< endl;
        return 1;
    }

    arquivo1.ignore(1000, '\n');
    cout << "estado antes da leitura: " << arquivo1.good() << endl;
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

    Energias(eventos);


}