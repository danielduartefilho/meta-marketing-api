import os
import requests
import json
from datetime import datetime
from typing import Dict, Optional, Any
import sys

class MetaAPITester:
    def __init__(self):
        self.base_url = "https://graph.facebook.com/v22.0"
        self.access_token = os.getenv("META_ACCESS_TOKEN")
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        self.rate_limits = {
            "points": 0,
            "total": 9000,
            "window": 300  # 5 minutes
        }
        self.cache = {}

    def _update_rate_limits(self, response: requests.Response) -> None:
        """Atualiza o controle de rate limits baseado nos headers da resposta"""
        usage = response.headers.get("X-Business-Use-Case-Usage")
        if usage:
            try:
                usage_data = json.loads(usage)
                self.rate_limits["points"] = usage_data.get("points", 0)
            except:
                pass

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Processa a resposta e extrai métricas importantes"""
        self._update_rate_limits(response)
        
        metrics = {
            "status_code": response.status_code,
            "response_time": response.elapsed.total_seconds(),
            "rate_limit_points": self.rate_limits["points"],
            "cache_hit": response.headers.get("X-FB-Debug-Cache", "0") == "1"
        }
        
        try:
            data = response.json()
            metrics["data_complete"] = True
            if "error" in data:
                metrics["error"] = data["error"]
                metrics["data_complete"] = False
            return metrics, data
        except:
            metrics["data_complete"] = False
            return metrics, None

    def test_endpoint(self, endpoint: str, method: str = "GET", 
                     params: Optional[Dict] = None) -> None:
        """Testa um endpoint específico com métricas e validações"""
        url = f"{self.base_url}{endpoint}"
        print(f"\n=== Testando {method} {endpoint} ===")
        
        try:
            # Faz a requisição
            if method == "GET":
                response = requests.get(url, headers=self.headers, params=params)
            else:
                response = requests.post(url, headers=self.headers, json=params)
            
            # Processa a resposta
            metrics, data = self._handle_response(response)
            
            # Exibe métricas
            print(f"Status: {metrics['status_code']}")
            print(f"Tempo de resposta: {metrics['response_time']:.3f}s")
            print(f"Rate limit usado: {metrics['rate_limit_points']}/{self.rate_limits['total']}")
            print(f"Cache hit: {'Sim' if metrics['cache_hit'] else 'Não'}")
            print(f"Dados completos: {'Sim' if metrics['data_complete'] else 'Não'}")
            
            # Exibe dados ou erro
            if "error" in metrics:
                print("\nErro:", json.dumps(metrics["error"], indent=2))
            elif data:
                print("\nResposta:", json.dumps(data, indent=2))
            
            return data
            
        except Exception as e:
            print(f"Erro na requisição: {str(e)}")
            return None

    def run_tests(self) -> None:
        """Executa a suíte completa de testes"""
        print("=== Iniciando testes da API ===")
        print(f"Data/Hora: {datetime.now()}")
        print(f"Versão da API: v22.0")
        
        # 1. Test insights endpoint
        print("\n1. Testando endpoint de insights")
        print("\n=== Testando GET /act_906594379912215/insights ===")
        
        insights_response = requests.get(
            f"{self.base_url}/act_906594379912215/insights",
            headers=self.headers,
            params={
                "level": "campaign",
                "fields": "impressions,reach,spend,inline_link_clicks",
                "date_preset": "last_30d"
            }
        )
        
        print(f"Status: {insights_response.status_code}")
        print(f"Tempo de resposta: {insights_response.elapsed.total_seconds():.3f}s")
        print(f"Rate limit usado: {insights_response.headers.get('X-Business-Use-Case-Usage', '0/9000')}")
        print(f"Cache hit: {'Sim' if insights_response.headers.get('X-FB-Debug-Cache', 'miss') == 'hit' else 'Não'}")
        
        if insights_response.status_code == 200:
            insights_data = insights_response.json()
            if insights_data.get("data"):
                print("\nMétricas encontradas:")
                for metric in insights_data["data"]:
                    print(f"- Impressões: {metric.get('impressions', '0')}")
                    print(f"- Alcance: {metric.get('reach', '0')}")
                    print(f"- Gasto: {metric.get('spend', '0')}")
                    print(f"- Cliques: {metric.get('inline_link_clicks', '0')}")
            else:
                print("Nenhuma métrica encontrada no período")
        else:
            print(f"Erro: {insights_response.status_code}")
            print(insights_response.text)
            
        # 2. Test trends endpoint
        print("\n2. Testando endpoint de trends")
        print("\n=== Testando GET /act_906594379912215/trends/performance ===")
        
        trends_response = requests.get(
            f"{self.base_url}/act_906594379912215/trends/performance",
            headers=self.headers,
            params={
                "date_preset": "last_30d"
            }
        )
        
        print(f"Status: {trends_response.status_code}")
        print(f"Tempo de resposta: {trends_response.elapsed.total_seconds():.3f}s")
        print(f"Rate limit usado: {trends_response.headers.get('X-Business-Use-Case-Usage', '0/9000')}")
        print(f"Cache hit: {'Sim' if trends_response.headers.get('X-FB-Debug-Cache', 'miss') == 'hit' else 'Não'}")
        
        if trends_response.status_code == 200:
            trends_data = trends_response.json()
            print("\nTrends encontrados:")
            if trends_data.get("data"):
                if trends_data["data"].get("best_performing_creatives"):
                    print(f"- {len(trends_data['data']['best_performing_creatives'])} criativos de melhor performance")
                if trends_data["data"].get("best_performing_audiences"):
                    print(f"- {len(trends_data['data']['best_performing_audiences'])} segmentos de público de melhor performance")
            else:
                print("Nenhum trend encontrado no período")
        else:
            print(f"Erro: {trends_response.status_code}")
            print(trends_response.text)

def validate_token():
    """Validate if token has required permissions"""
    try:
        response = requests.get(
            "https://graph.facebook.com/v22.0/me/permissions",
            headers={"Authorization": f"Bearer {os.getenv('META_ACCESS_TOKEN')}"}
        )
        if response.status_code == 200:
            permissions = response.json().get("data", [])
            required = {"ads_read"}  # Apenas ads_read é necessário
            granted = {p["permission"] for p in permissions if p["status"] == "granted"}
            missing = required - granted
            if missing:
                print("\nERRO: Token não tem a permissão necessária.")
                print(f"Permissão faltando: {missing}")
                print("\nPermissões concedidas:")
                for p in granted:
                    print(f"- {p}")
                return False
            print("\nPermissão validada com sucesso:")
            for p in granted:
                print(f"- {p}")
            return True
        else:
            print(f"\nERRO: Token inválido ou expirado (Status: {response.status_code})")
            print(response.text)
            return False
    except Exception as e:
        print(f"\nERRO ao validar token: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Iniciando testes da API ===")
    print(f"Data/Hora: {datetime.now()}")
    print(f"Versão da API: v22.0")
    
    if not os.getenv("META_ACCESS_TOKEN"):
        print("\nERRO: Token de acesso não encontrado!")
        print("Defina a variável de ambiente META_ACCESS_TOKEN")
        sys.exit(1)
    
    if not validate_token():
        sys.exit(1)
        
    try:
        tester = MetaAPITester()
        tester.run_tests()
    except Exception as e:
        print(f"\nERRO durante os testes: {str(e)}")
        sys.exit(1)
