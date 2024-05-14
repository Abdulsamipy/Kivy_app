import ssl
ssl._create_default_https_context = ssl._create_stdlib_context

from kivymd.app import MDApp
from kivymd.uix.screen import Screen
from kivymd.uix.list import  OneLineAvatarIconListItem
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from functools import partial
from kivymd.uix.list import ImageLeftWidget
from kivy.uix.gridlayout import GridLayout
from kivymd.uix.label import MDLabel
import shopify
import threading
from kivy.lang import Builder
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRoundFlatButton, MDFillRoundFlatIconButton
from kivy.properties import ListProperty, StringProperty
from kivy.uix.splitter import Splitter
from kivymd.uix.toolbar import MDTopAppBar
import mysql.connector


class TestApp(MDApp):
    Builder.load_file('Test.kv')
    screen1 = Screen(name='screen1')
    screen2 = Screen(name='screen2')
    def get_all_orders(self):
        API_KEY = ''
        API_PASSWORD = ''
        access_token = ''
        shop_url = '.myshopify.com'
        version = '2023-01'
        url = ''
        self.session = shopify.Session(shop_url, version, access_token)
        shopify.ShopifyResource.activate_session(self.session)
        orders = shopify.Order.find()
        # Create a dictionary to store order information
        #print(orders)
        order_info = {}
        # Iterate through each order and retrieve the required information
        for order in orders:
            
            order_number = order.name
            order_Id = order.id
            try:
                customer_name = order.customer.first_name + ' ' + order.customer.last_name
            except:
                customer_name = ''
            fulfillment_status = order.fulfillment_status
            shipping_lines = order.shipping_lines
            for shipping_line in shipping_lines:
                self.shipping_price = shipping_line.price
                
            order_products = []
            # Iterate through each line item and retrieve the product details
            for line_item in order.line_items:
                product_name = line_item.name
                product_price = line_item.price
                product_sku = line_item.sku
                product_qty = line_item.quantity
                #print(product_qty)
                order_products.append({
                    'name': product_name,
                    'price': product_price,
                    'sku': product_sku,
                    'qty': product_qty
                })
            total_price = order.total_price
            # Add the order information to the dictionary
            order_info[order_Id] = {
                'order_number': order_number,
                'order_id': order_Id,
                'customer_name': customer_name,
                'fulfillment_status': fulfillment_status,
                'products': order_products,
                'total_price': total_price,
                'Shipping_cost': self.shipping_price
            }
        
        return order_info
    
    def mark_paid(self, order_idd):
        print(f"Marking order as paid: {order_idd}")
        trans = shopify.Transaction.find_first(order_id=order_idd)
       # print(trans.order_id)
        new_transaction = shopify.Transaction()
        #new_transaction.currency = "CAD";
        new_transaction.kind = "capture" 
        #new_transaction.status = "paid" 
        #new_transaction.gateway = "manual" 
        new_transaction.amount = self.total_price
        new_transaction.parent_id = trans.id
        new_transaction._prefix_options ={"order_id" : order_idd}
        new_transaction.save()
            
    def fullfull_order(self, order_idd):
        t = threading.Thread(target=self.mark_paid, args=(order_idd))
        t.start()

        print(f"fullfilling order: {order_idd}")
        shopify.Fulfillment._prefix_source = ''
        new_orders = shopify.Order.find()
        for order in new_orders:
            fo = shopify.FulfillmentOrders.find(order_id=order.id)[0]
            if str(fo.order_id) == str(order_idd):
            
                location = fo.assigned_location_id
                for i in fo.line_items:
                    fulfillment = shopify.Fulfillment({
                        'order_id':fo.order_id,
                        })
                    fulfillment.location_id = location
                    fulfillment.notify_customer = False
                    fulfillment.message = 'The package has been Delivered'

                    fulfillment.line_items_by_fulfillment_order = [
                    {
                        "fulfillment_order_id": fo.id,
                        "fulfillment_order_line_items": [
                        {
                            "id": i.id,
                            "quantity": i.fulfillable_quantity
                        }
                        ]
                    }
                    ]
                    fulfillment.save()                
        shopify.ShopifyResource.clear_session()
        
        
    def build(self):
        self.theme_cls.primary_palette = "Green"
        # Create the screen manager
        self.screen_manager = ScreenManager(transition=SlideTransition())

        # Create the screens
        self.screen1 = Screen(name='screen1')
        self.screen2 = Screen(name='screen2')
        
        # Create a BoxLayout for the OneLineListItems
        box_layout = BoxLayout(orientation='vertical', spacing=10, padding=10, size_hint_y=None)
        box_layout.bind(minimum_height=box_layout.setter('height'))
        
        screen1_toolbar = MDTopAppBar(
                        title='Home - Order List',
                        pos_hint={'top': 1},
                        elevation=0,
                        left_action_items=[
                            ["menu", lambda x: None]
                        ],
                        right_action_items=[
                            ["bell", lambda x: None],
                            ["dots-vertical", lambda x: None],
                        ],
                        md_bg_color=self.theme_cls.primary_color,
                        background_palette='Primary',
                        background_hue='500',
                    )
        screen1_toolbar.specific_text_color = (1, 1,1, 1)
        box_layout.add_widget(screen1_toolbar)
        
        order_info = self.get_all_orders()
        # Create the OneLineListItems and bind the on_press function
        for order_Id, order_data in order_info.items():
            item = OneLineAvatarIconListItem(ImageLeftWidget(source="Images/green.png") ,text=f"Order ID: {order_data['order_number']}" )
            item.on_press = partial(self.show_screen2, f"{order_data['order_number']}", order_data)
            box_layout.add_widget(item)
    
        # Add the BoxLayout to a ScrollView
        scroll_view = ScrollView()
        scroll_view.add_widget(box_layout)

        # Add the ScrollView to Screen 1
        self.screen1.add_widget(scroll_view)

        # Add the screens to the screen manager
        self.screen_manager.add_widget(self.screen1)
        self.screen_manager.add_widget(self.screen2)

        # Set the starting screen
        self.screen_manager.current = 'screen1'

        return self.screen_manager
    

            
    def on_back(self):
        self.screen_manager.current = 'screen1'

        
    def insert_record(self, order_id, total_cost, shipment, profit, purchase):
        # establish a connection to the MySQL server
        mydb = mysql.connector.connect(
            host="c03.tmdcloud.eu",
            user="ghurocom_Greenlifeksa_db",
            password="Files123..",
            database="ghurocom_Greenlife_order"
        )

        # create a cursor object to execute SQL queries
        mycursor = mydb.cursor()

        # check if the Order_id already exists
        sql_check = "SELECT COUNT(*) FROM GL_Profit WHERE Order_Id = %s"
        val_check = (order_id,)
        mycursor.execute(sql_check, val_check)
        result = mycursor.fetchone()

        # if Order_id exists, update the record
        if result[0] > 0:
            sql = "UPDATE GL_Profit SET Total_Cost = %s, Shipment = %s, Purchase_Cost = %s, Profit = %s WHERE Order_Id = %s"
            val = (total_cost, shipment, purchase, profit, order_id)
        # if Order_id does not exist, insert a new record
        else:
            sql = "INSERT INTO GL_Profit (Order_Id, Total_Cost, Shipment, Purchase_Cost, Profit) VALUES (%s, %s, %s, %s, %s)"
            val = (order_id, total_cost, shipment, purchase, profit)

        # execute the SQL query
        mycursor.execute(sql, val)

        # commit the changes to the database
        mydb.commit()

        # print a success message
        print(mycursor.rowcount, "record(s) inserted or updated.")


    
    def show_screen2(self, order_Number, Order_data):
        self.total_cal_price = "0"
        self.order_total = float(Order_data['total_price'])
        self.order_num = order_Number
        self.screen2.clear_widgets() 
        # Clear any existing widgets in screen
        
         # Create toolbar and add it to the screen
        screen2_toolbar = MDTopAppBar(
                        title=f'Order Number : {order_Number}',
                        pos_hint={'top': 1},
                        elevation=0,
                        md_bg_color=self.theme_cls.primary_color,
                        background_palette='Primary',
                        background_hue='500',
                        top=True
                    )
        screen2_toolbar.specific_text_color = (1, 1,1, 1)
        screen2_toolbar.left_action_items = [["arrow-left", lambda x: self.on_back()]]
        
        scroll_view = ScrollView()
        
        # Create a GridLayout to display the order details
        self.grid_layout = GridLayout(cols=2, spacing=10, padding=10)
        self.grid_layout.cols = 1
        self.grid_layout.spacing = 10
        self.grid_layout.padding = 10
        self.grid_layout.size_hint_y = None
        self.grid_layout.bind(minimum_height=self.grid_layout.setter('height'))
        
        
        
        self.grid_layout.add_widget(screen2_toolbar)
        
        customer_layout = GridLayout(cols=2, spacing=10, size_hint_y=None, height=50)   
        customer_layout.add_widget(MDLabel(text='Customer Name:', font_size=20, bold=True))
        customer_layout.add_widget(MDLabel(text=Order_data['customer_name'], font_size=20))
        self.grid_layout.add_widget(customer_layout)

        splitter1 = Splitter(size_hint_y=None, height=5)
        self.grid_layout.add_widget(splitter1)

        product_layout = GridLayout(cols=2, spacing=10, size_hint_y=None, height=50)
        product_layout.add_widget(MDLabel(text='Product List:', font_size=20, bold=True))
        product_layout.add_widget(MDLabel(text='', font_size=20))
        self.grid_layout.add_widget(product_layout)

        splitter2 = Splitter(size_hint_y=None, height=5)
        self.grid_layout.add_widget(splitter2)
        splitter6 = Splitter(size_hint_y=None, height=5)
        self.grid_layout.add_widget(splitter6)
        self.product_prices = []  # Store the input values in a list
        self.total_price = '0'
        # Add the product details to the GridLayout
        for product in Order_data['products']:
            #print(product)
            product_name_label = MDLabel(text=f"{product['name']} (Price: {product['price']} SR)  (QTY: {product['qty']})", font_size=16)
            self.grid_layout.add_widget(product_name_label)

            p = MDTextField(text='', hint_text='Enter Price You Got From Supplier (total amount for all quantity)', input_filter='int', multiline=False, size_hint=(.134, None), height=50)
            self.grid_layout.add_widget(p)
            self.product_prices.append(p)  # Add the input instance to the list of product prices

        splitter3 = Splitter(size_hint_y=None, height=5)
        self.grid_layout.add_widget(splitter3)

        total_layout = GridLayout(cols=2, spacing=10, size_hint_y=None, height=50)
        total_layout.add_widget(MDLabel(text='Total Price:', font_size=20, bold=True))
        self.cost = float(self.order_total) - float(Order_data['Shipping_cost'])
        
        total_layout.add_widget(MDLabel(text=f"{round(float(self.cost), 2)} SR", font_size=20))
        self.grid_layout.add_widget(total_layout)

        splitter4 = Splitter(size_hint_y=None, height=5)
        self.grid_layout.add_widget(splitter4)

        button = MDRoundFlatButton(text='Calculate Profit', on_press=self.get_price, size_hint_y=None, height=50)
        self.grid_layout.add_widget(button)

        splitter5 = Splitter(size_hint_y=None, height=5)
        self.grid_layout.add_widget(splitter5)

        profit_layout = GridLayout(cols=2, spacing=10, size_hint_y=None, height=50)
        
        profit_layout.add_widget(MDLabel(text='Profit:', font_size=20, bold=True))
        self.profit_lable = MDLabel(text=str(self.total_cal_price) , font_size=20)
        profit_layout.add_widget(self.profit_lable)
        self.grid_layout.add_widget(profit_layout)
        

            
        
        submit = MDFillRoundFlatIconButton(text='Order FullFilled',  text_color= "white",  _doing_ripple=True,)
        submit.on_press = partial(self.fullfull_order,  Order_data['order_id'])
       # submit.on_press = on_press_wrapper(self)
        self.grid_layout.add_widget(submit)

        try:
            scroll_view.add_widget(self.grid_layout)
        except Exception as e:
            print(e)
        # Add the GridLayout to the screen2
        
        self.screen2.add_widget(scroll_view)

        # Set the current screen as screen2
        self.screen_manager.current = 'screen2'
    

        
    def get_price(self, button_instance):
        self.total_price1 = sum(int(p.text) for p in self.product_prices)

        self.calulcated_profit = float(self.cost) - float(self.total_price1)
        self.total_cal_price = str(self.calulcated_profit)  # Update the value of self.total_price
        round_num = round(float(self.total_cal_price), 2)
        self.profit_lable.text = str(round_num)
        print(f"Profit on  Order: {self.order_num}, total order: {self.order_total}, profit: {round_num}, shippment: {self.shipping_price}")
        print(self.order_num)
        
        #self.insert_record(str(self.order_num), self.cost, self.shipping_price, round_num, self.total_price1)
        t = threading.Thread(target=self.insert_record, args=(str(self.order_num), self.cost, self.shipping_price, round_num, self.total_price1))
        t.start()

                    
if __name__ == '__main__':
    TestApp().run()
