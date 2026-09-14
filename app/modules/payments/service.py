import urllib.request
import json
from app.core.config import Config

class PaywuzService:
    @staticmethod
    def create_qris_transaction(order_id: str, amount: float):
        url = f"{Config.PAYWUZ_API_URL}/transactions"
        
        payload = {
            "orderId": order_id,
            "amount": int(amount),
            "paymentMethod": "QRIS"
        }
        
        data = json.dumps(payload).encode('utf-8')
        
        req = urllib.request.Request(url, data=data, method='POST')
        req.add_header('Authorization', f'Bearer {Config.PAYWUZ_API_KEY}')
        req.add_header('Content-Type', 'application/json')
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
        
        try:
            with urllib.request.urlopen(req) as response:
                res_body = response.read().decode('utf-8')
                res_json = json.loads(res_body)
                return res_json.get('data', {})
        except urllib.error.HTTPError as e:
            err_body = e.read().decode('utf-8')
            raise ValueError(f"Paywuz API Error: {e.code} - {err_body}")
        except Exception as e:
            raise ValueError(f"Failed to connect to Paywuz: {str(e)}")
