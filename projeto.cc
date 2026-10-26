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

int main (){

    //lendo o arquivo de eventos e devolvendo o arquivo com as coordenadas galaticas
    ifstream entrada("Eventos.txt");
    ofstream saida("eventos_galaticos.txt");

    if (!entrada){
        cerr << "erro ao abrir eventos.txt" << endl;
        return 1;
    }

    if (!saida){
        cerr << "erro ao abrir eventos_galaticos.txt" << endl;
        return 1;
    }

    //cabeçalho do arquivo de saída
    saida << "# AugId l b Ecor UTC Theta Phi T5 FTR \n" << endl;

    long long augId;
    double dec, ra, ecor, theta, phi, UTC, t5, ftr;
    double l, b;

    string linha;

    while (getline(entrada, linha)) {

            cout << "linha lida: [" << linha << "]" << augId << endl;
        
        stringstream ss(linha);

        if (ss >> augId >> dec >> ra >> ecor >> UTC >> theta >> phi >> t5 >> ftr) {
        cout << "LEITURA DOS 9 VALORES OK!" << endl;
        cout << "AugId = " << augId << endl;
        cout << "Dec   = " << dec << endl;
        cout << "RA    = " << ra << endl;
        
        CoordenadasGalaticas galaticas =
        CoordenadaEquatorialGalatica(ra, dec);

        cout << "l = " << galaticas.l << endl;
        cout << "b = " << galaticas.b << endl;

        saida << augId << " "
          << galaticas.l << " "
          << galaticas.b << " "
          << ecor << " "
          << UTC << " "
          << theta << " "
          << phi << " "
          << t5 << " "
          << ftr << endl;

        }
        else {
        cout << "ERRO AO CONVERTER ESTA LINHA!" << endl;
        }
    }

    entrada.close();
    saida.close();
    cout << "conversão feita de (ra,dec) para (l,b) " << endl;
    return 1;

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









}