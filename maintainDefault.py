"""
Updates the default strap selection for all ski pole products
"""
import requests
import textNotifier

class DefaultUpdater:
    def __init__(self):
        self.storeId = '7476261'
        self.ogspId = '55001151'
        self.tspId = '74102380'
        self.rtspId = '506210440'
        self.trekppId = '570262509'
        self.kidsspId = '94782479'
        self.token = ''

    def updateDefaultStrap(self):
        """
        Updates the default strap selection to index 1 for all products
        """
        try:
            productIds = [self.ogspId, self.tspId, self.rtspId, self.trekppId, self.kidsspId]
            
            for productId in productIds:
                try:
                    # Get current product data
                    data = self.getProduct(productId)
                    
                    # Update the default choice for Strap option
                    options = data['options']
                    for option in options:
                        if option['name'] == 'Strap':
                            option['defaultChoice'] = 1
                    
                    # Update the product
                    url = f"https://app.ecwid.com/api/v3/{self.storeId}/products/{productId}"

                    headers = {
                        "accept": "application/json",
                        "Authorization": f"Bearer {self.token}",
                        "content-type": "application/json"
                    }

                    response = requests.put(url, headers=headers, json=data)
                    print(f"Updated default strap for product {productId}: {response.text}")
                    
                except Exception as e:
                    error_msg = f"Error updating product {productId}: {str(e)}"
                    print(error_msg)
                    textNotifier.send_message(7572020009,'tmobile', error_msg)
                    
        except Exception as e:
            error_msg = f"Critical error in updateDefaultStrap: {str(e)}"
            print(error_msg)
            textNotifier.send_message(6103246241,'tmobile', error_msg)

    def getProduct(self, productId):
        """
        Get product based on productId
        input: productId
        output: product json data
        """
        try:
            url = f"https://app.ecwid.com/api/v3/{self.storeId}/products/{productId}"

            headers = {
                "accept": "application/json",
                "Authorization": f"Bearer {self.token}"
            }

            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            return response.json()
            
        except Exception as e:
            error_msg = f"Error getting product {productId}: {str(e)}"
            print(error_msg)
            textNotifier.send_message(7572020009,'tmobile', error_msg)
            return None

if __name__ == '__main__':
    updater = DefaultUpdater()
    updater.updateDefaultStrap()
