#include <fstream>
#include <iomanip>
#include <iostream>
#include <vector>
#include <cmath>

using namespace std;

//const double Rad2Deg = 180./M_PI;
//const double Deg2Rad = M_PI/180.;

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

    vector<fontes> fonte;
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

        fonte.push_back(fontesTemp);
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
    //EventosStarburst(eventos, fonte);
}
