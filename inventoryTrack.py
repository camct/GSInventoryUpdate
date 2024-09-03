"""
Auto Inventory Update: Checks recent orders and updates mountain strap inventory, removing product options from website if necessary (out of stock)
Ecwid allowed API calls per minute: 600/min
Current API calls: O(5*(# or orders in a minute)) -- active cronjob running every minute
Author: Cabot McTavish
"""
import requests
import emailNotifier, textNotifier
from datetime import datetime

class ecwidCall:
    def __init__(self):
        self.sku=''
        self.name=''
        self.quantity=''
        self.storeId='7476261'
        self.ogspId='55001151'
        self.tspId='74102380'
        self.rtspId='506210440'
        self.trekppId='570262509'
        self.kidsspId='94782479'
        self.mtnStrapId='116311087'
        self.token=''
    def getFromEcwid(self,productId,variationId):
        url = f"https://app.ecwid.com/api/v3/{self.storeId}/products/{productId}/combinations/{variationId}"

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.token}"
        }

        response = requests.get(url, headers=headers)
        # print(response.json())

    def postToEcwid(self,jsonData,amountPurchased,mtnStrap):
        """
        Update Ecwid mountain strap inventories
        """

        f.write("Stock quantity of " + mtnStrap + " was " + str(jsonData['quantity']) + ". It is being updated to " + str(jsonData['quantity']-amountPurchased) + ".")
        jsonData['quantity']-=amountPurchased
        if jsonData['quantity']<=0:
            productIds = [self.ogspId,self.tspId,self.rtspId,self.trekppId,self.kidsspId]
            f.write(str(mtnStrap) + " is out of stock.\n")
            for productId in productIds:
                data=x.getProduct(productId)
                x.deleteOptionValue(data,mtnStrap,productId)
            if jsonData['quantity']<0:
                f.write(mtnStrap + " was purchased over stock!!!\n")
                msg = f"{mtnStrap} was purchased over stock"
                textNotifier.send_message(6103246241,'tmobile',msg)
                emailNotifier.send_email('andrew@grasssticks.com',msg)

        variationId=jsonData['id']

        url = f"https://app.ecwid.com/api/v3/{self.storeId}/products/{self.mtnStrapId}/combinations/{variationId}" # this needs to be my correct path

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.token}",
            "content-type": "application/json"
        }

        response = requests.put(url, headers=headers, json=jsonData)
        f.write("Stock quantity for " + str(mtnStrap) + " was decreased by " + str(amountPurchased) + "\n")

        print(response.text)

    def updateVis(self,strapType):
        """
        NOT WORKING -- Dont run
        """
        # // CSS to make option invisible on both mtn straps and original grass sticks (visible/hidden)
        x='.form-control--radio.form-control.form-control--flexible.details-product-option--{mtnStrapType} {visibility:hidden}'

    def getVariationIDs(self, id):
        """
        Input product ID as id and it returns a dictionary of all the mtn strap inventories -- {Mtn Strap : Variation JSON}
        """
        url = f"https://app.ecwid.com/api/v3/{self.storeId}/products/{id}/combinations"

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.token}"
        }

        response = requests.get(url, headers=headers)

        curr=response.json()
        idTable=dict()
        for i in range(len(curr)):
            # print(curr[i])
            # print("")
            name=curr[i]['options'][0]['value']
            # sku=curr[i]['sku']
            # id=curr[i]['id']
            # quantity=curr[i]['quantity']

            if name not in idTable: idTable[name]=curr[i]
            # idTable[name]['sku']=sku
            # idTable[name]['id']=id
            # idTable[name]['quantity']=quantity

        return idTable

    def getOrders(self, time1, time2):
        """
        Get all mountain strap purchases between time1 and time2
        input: time1=later time, time2=earlier time
        output: all of the mountain straps that have been ordered from the ski poles and how many
        """

        url = f"https://app.ecwid.com/api/v3/{self.storeId}/orders?createdFrom={time2}&createdTo={time1}"
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.token}"
        }

        response = requests.get(url, headers=headers)
        orderlst=response.json()['items']
        productIds = [self.ogspId,self.tspId,self.rtspId,self.trekppId,self.kidsspId]

        # print(orderlst[1])
        straps=dict()
        for order in range(len(orderlst)):
            products=orderlst[order]['items']
            for product in range(len(products)):
                productId = products[product]['productId']
                if str(productId) in productIds:
                    options = products[product]['selectedOptions']
                    for option in options:
                        if option['name']=='Strap' and option['value']!='None' and option['value']!='Fixed' and option['value']!='Adjustable': 
                            if (option['value'],productId) not in straps: straps[(option['value'],productId)]=0
                            straps[(option['value'],productId)]+=1
        return straps

    def getProduct(self,productId):
        """
        Get product based on productId
        input: productId
        output: product json data
        """

        url = f"https://app.ecwid.com/api/v3/{self.storeId}/products/{productId}"

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.token}"
        }

        response = requests.get(url, headers=headers)
        return response.json()

    def deleteOptionValue(self, jsonData,strap,productId):
        """
        If we are out of a mountain strap, it will be deleted from the original grass sticks customizable strap option list.
        input: Product json data, mountain strap name
        """
        
        options=jsonData['options']
        indexToRemove=float('inf')
        for i in range(len(options)):
            if options[i]['name']=='Strap':
                choices=options[i]['choices']
                for j in range(len(choices)):
                    if choices[j]['text']==strap: 
                        indexToRemove=j
                        break
                if indexToRemove!='inf': 
                    del choices[indexToRemove]
                    f.write(str(strap) + " was deleted from Original Grass Sticks option values\n")
                break

        url = f"https://app.ecwid.com/api/v3/{self.storeId}/products/{productId}"

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.token}",
            "content-type": "application/json"
        }

        response = requests.put(url, headers=headers, json=jsonData)
        f.write(strap + " was deleted from the " + str(jsonData['name']) + " listing.")

        print(response.text)

    def updateOptionValues(self):
        """
        Updates product option value availability for all products based on mtn strap inventory.
        """
        productIds = [self.ogspId,self.tspId,self.rtspId,self.trekppId,self.kidsspId]
        for productId in productIds:
            jsonData=self.updateJsonForRestock(productId)
            url = f"https://app.ecwid.com/api/v3/{self.storeId}/products/{productId}"

            headers = {
                "accept": "application/json",
                "Authorization": f"Bearer {self.token}",
                "content-type": "application/json"
            }

            response = requests.put(url, headers=headers, json=jsonData)

            print(response.text)
    
    def updateJsonForRestock(self, productId):
        """
        Updates option value data based on mtn strap inventory.
        """
        data=self.getProduct(productId)

        kidFactor=(productId==self.kidsspId)
        strapsInInventory=dict()
        mtnStrapInventory=self.getVariationIDs(self.mtnStrapId)
        for i in mtnStrapInventory:
            if mtnStrapInventory[i]['quantity']>0:
                if (i!='Mary Jane'):
                    strapsInInventory[i]=1

        currentStraps=dict()
        options=data['options']
        for option in range(len(options)):
            if options[option]['name']=='Strap':
                choices=options[option]['choices']
                for choice in range(len(choices)):
                    currentStraps[choices[choice]['text']]=1


        for strap in strapsInInventory:
            if strap not in currentStraps:
                f=open('inventoryUpdateLog.txt', 'a')
                f.write('----------------------\n')
                f.write(f'{strap} was added to all ski pole products')
                newOption=dict()
                newOption['text']=strap
                newOption['priceModifier']=18
                newOption['priceModifierType']='ABSOLUTE'
                newOption['textTranslated']={'de':'','es_419':'','ja':'','en':f'{strap}', 'fr':'','es':''}
                for i in range(len(options)):
                    if options[i]['name']=='Strap':
                        choices=options[i]['choices']
                        choices.append(newOption)
                f.close()
        
        # for i in range(len(options)):
        #     if options[i]['name']=='Strap':
        #         choices=(options[i]['choices'])
        #         for choice in range(len(choices)):
        #             print(choices[choice])
        return data

if __name__=='__main__':    

    x=ecwidCall()

    # -----Get my unix timestamp
    now=datetime.now()
    time=round(datetime.timestamp(now))

    # -----Get orders from past interval
    interval=1000000
    orders=x.getOrders(str(time),str(time-interval))
    print(orders)

    # if orders:
	# # -----Write to a file
    #     unixTimeStamp = datetime.fromtimestamp(time-interval)
    #     f=open('inventoryUpdateLog.txt', 'a')
    #     f.write("----------------------\n")
    #     f.write("Orders from " + str(unixTimeStamp) + " to " + str(now) + "\n")

    #     # -----Get all mountain strap variation IDs and their stock quantity
    #     quantities=x.getVariationIDs(x.mtnStrapId)

    #     # -----Update these orders (If stock quantity is 0, will be removed from original grass sticks list)
    #     for i in orders:
    #         json=quantities[i[0]]
    #         amount=orders[i]
    #         strapName=i[0]
    #         f.write("Order id is " + str(json['id']) + " and productId is " + str(i[1]) + ".\n")
    #         x.postToEcwid(json,amount,strapName)
    #     f.close()

