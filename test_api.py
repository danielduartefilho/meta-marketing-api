import os
import requests
import json
from datetime import datetime
from typing import Dict, Optional, Any

class MetaAPITester:
    def __init__(self):
        self.base_url = "https://graph.facebook.com/v22.0"
        self.access_token = os.getenv("META_ACCESS_TOKEN")
        self.headers = {"Authorization": f"Bearer {self.access_token}"}
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
        
        # 1. Listar contas de anúncio
        print("\n1. Testando listagem de contas")
        accounts = self.test_endpoint(
            "/me/adaccounts",
            params={"fields": "id,name,account_status"}
        )
        
        if accounts and "data" in accounts and accounts["data"]:
            account = accounts["data"][0]
            account_id = account["id"].replace("act_", "")
            
            # 2. Listar campanhas da conta
            print("\n2. Testando listagem de campanhas")
            campaigns = self.test_endpoint(
                f"/act_{account_id}/campaigns",
                params={
                    "fields": "id,name,status,objective",
                    "limit": 25
                }
            )
            
            if campaigns and "data" in campaigns and campaigns["data"]:
                campaign = campaigns["data"][0]
                campaign_id = campaign["id"]
                
                # 3. Detalhes da campanha
                print("\n3. Testando detalhes da campanha")
                self.test_endpoint(
                    f"/{campaign_id}",
                    params={
                        "fields": "id,name,status,objective,daily_budget,lifetime_budget,bid_strategy"
                    }
                )
                
                # 4. Listar conjuntos de anúncios
                print("\n4. Testando listagem de conjuntos de anúncios")
                adsets = self.test_endpoint(
                    f"/act_{account_id}/adsets",
                    params={
                        "fields": "id,name,targeting,daily_budget,lifetime_budget,status,bid_strategy,billing_event",
                        "breakdowns": "age,gender,region",
                        "limit": 25
                    }
                )
                
                if adsets and "data" in adsets and adsets["data"]:
                    adset = adsets["data"][0]
                    adset_id = adset["id"]
                    
                    # 5. Detalhes do conjunto de anúncios
                    print("\n5. Testando detalhes do conjunto de anúncios")
                    self.test_endpoint(
                        f"/{adset_id}",
                        params={
                            "fields": "id,name,targeting,daily_budget,lifetime_budget,status,bid_strategy,billing_event"
                        }
                    )
                
                # 6. Listar anúncios da campanha
                print("\n6. Testando listagem de anúncios")
                ads = self.test_endpoint(
                    f"/act_{account_id}/ads",
                    params={
                        "campaign_id": campaign_id,
                        "fields": "id,name,creative{id,title,body,image_url,video_id,thumbnail_url},status,effective_status,preview_shareable_link",
                        "limit": 25
                    }
                )
                
                if ads and "data" in ads and ads["data"]:
                    ad = ads["data"][0]
                    ad_id = ad["id"]
                    
                    # 7. Métricas de performance do anúncio
                    print("\n7. Testando métricas do anúncio")
                    self.test_endpoint(
                        f"/act_{account_id}/insights",
                        params={
                            "level": "ad",
                            "fields": "impressions,inline_link_clicks,inline_link_click_ctr,actions,video_p25_watched_actions,video_p50_watched_actions,video_p75_watched_actions,video_p95_watched_actions,video_p100_watched_actions",
                            "date_preset": "last_30d",
                            "filtering": json.dumps([{
                                "field": "ad.id",
                                "operator": "EQUAL",
                                "value": ad_id
                            }])
                        }
                    )
                
                # 8. Insights da campanha
                print("\n8. Testando insights")
                self.test_endpoint(
                    f"/act_{account_id}/insights",
                    params={
                        "level": "campaign",
                        "fields": "impressions,reach,spend",
                        "date_preset": "last_7d",
                        "filtering": json.dumps([{
                            "field": "campaign.id",
                            "operator": "EQUAL",
                            "value": campaign_id
                        }])
                    }
                )

if __name__ == "__main__":
    if not os.getenv("META_ACCESS_TOKEN"):
        print("Erro: Configure a variável de ambiente META_ACCESS_TOKEN")
    else:
        tester = MetaAPITester()
        tester.run_tests()
