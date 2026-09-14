#include <fstream>
#include <iomanip>
#include <iostream>
#include <vector>
#include <cmath>

using namespace std;

const double Rad2Deg = 180./M_PI;
const double Deg2Rad = M_PI/180.;

struct Eventos {
    double l;
    double b;
};

struct fontes {
    double fontesl;
    double fontesb;
    double distancia;
    double utc;
};
double RadiansToDegree(double ValueRadians){
    return ValueRadians*Rad2Deg;
}

double ComputeAngularDistance(double lpoint1, double lpoint2, double bpoint1, double bpoint2){
    double Distance = sin (bpoint1) * sin(bpoint2) + cos(bpoint1) * cos(bpoint2) * cos(lpoint1 - lpoint2);
    return RadiansToDegree(Distance);
}

double DegreeToRadians(double ValueDegree){
    return ValueDegree*Deg2Rad;
}


void EventosStarburst(const vector<Eventos>& eventos, const vector<fontes>& galaxias) {

    //ao invez de um inteiro, fazemos uma matriz, pra cada galaxias, temos 10 janelas angulares direfentes
     int numStarbursts [23][10]={0};    

    //faz um aruivo de saida
    ofstream arquivo("EventosStarburst.txt"); 

    //cabeçalho do arquivo de saida
    arquivo<< "fonte  10 graus  9  8  7  6  5  4  3  2  1" << endl;     

    //também estamos varrendo diferentes janelas angulares
    //faz mais sentido primeiro fixar galaxias e depois procurar eventos.
    for (int janelaAngular=1; janelaAngular<=10; janelaAngular++){  
        for (int IndexGal=0; IndexGal<galaxias.size(); IndexGal++){  
       
            for (int IndexEvt=0; IndexEvt<eventos.size(); IndexEvt++){

                double evtl = DegreeToRadians(eventos[IndexEvt].l);
                double evtb = DegreeToRadians(eventos[IndexEvt].b);

                double fontel = DegreeToRadians(galaxias[IndexGal].fontesl);
                double fonteb = DegreeToRadians(galaxias[IndexGal].fontesb);

                // calculo da distancia angular entre dois pontos na esfera celeste
                double angulo = ComputeAngularDistance(fontel, evtb, fontel, evtl);

                //tem q ter o -1 pq a primeira posição tem indice 0
                if (angulo <= janelaAngular) {
                    numStarbursts[IndexGal][janelaAngular-1]++;  
                }

            } // fim do for i

        } // fim do for j

    } //fim do for janelaAgular

    for(int IndexGal=0; IndexGal<galaxias.size(); IndexGal++){

        arquivo << IndexGal+1 << " ";

        for (int janelaAngular=9; janelaAngular>=0; janelaAngular--){
            arquivo  <<  numStarbursts[IndexGal][janelaAngular] << "  ";
        } 

        arquivo << endl;
    } // fim for j


} //fim do void
	



int main() {
    
    vector<Eventos> eventos;
    // colunas: l (graus), b (graus) coordenadas galacticas
    ifstream arquivo("Eventos-totais.txt");
    if (!arquivo) {
        cerr << "erro ao abrir o arquivo Eventos-totais" << endl;
        return 1;
    }
  
    while (!arquivo.eof()) {
      
        Eventos eventosTemp;

        arquivo >> eventosTemp.l
                >> eventosTemp.b;
                
        eventos.push_back(eventosTemp);
    }

    arquivo.close();

    vector<fontes> fontes;
    //colunas: L(grau), b(grau) , Distancia(Mpc), utc
    
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

        fontes.push_back(fontesTemp);
    }

    arquivo2.close();

    /*
    cout << "===========================================\n";
    cout << "  ANALISE DE EVENTOS DE RAIOS COSMICOS\n";
    cout << "===========================================\n\n";
    cout << "Arquivo lido com sucesso.\n";
    cout << "Quantidade de eventos carregados: " << eventos.size() << "\n";

    */
    //analisarEnergias(eventos);
    //analisarDirecoes(eventos);
    //contarEventosCenA(eventos);
    //EventosStarburst(eventos, fontes);
}
