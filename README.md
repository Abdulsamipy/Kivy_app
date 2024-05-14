# Kivy Shopify Order Tracking App

## Overview

This Kivy app is designed to work on Android and helps you track the amount at which items were purchased and mark orders as delivered on the Shopify dashboard. The app integrates with Shopify to fetch orders, calculate profits, and update order statuses.

## Features

- Fetches all orders from the Shopify store.
- Displays order details including customer name, products, and total price.
- Allows input of purchase prices for calculating profit.
- Marks orders as paid and fulfilled on the Shopify dashboard.
- Inserts order records into a MySQL database.

## Installation

### Requirements

- Python 3.x
- Kivy
- KivyMD
- Shopify API
- MySQL Connector

### Setup

1. **Clone the repository:**

   ```sh
   git clone <repository_url>
   cd <repository_directory>
   ```

2. **Install dependencies:**

   ```sh
   pip install kivy kivymd shopify mysql-connector-python
   ```

3. **Configure Shopify API:**

   Edit the `get_all_orders` method in the `TestApp` class to add your Shopify API credentials:

   ```python
   API_KEY = '<your_api_key>'
   API_PASSWORD = '<your_api_password>'
   access_token = '<your_access_token>'
   shop_url = '<your_shop_url>.myshopify.com'
   version = '2023-01'
   ```

4. **Create the Kivy layout file:**

   Create a file named `Test.kv` with your desired layout. Here is a basic example:

   ```kv
   # Test.kv

   ScreenManager:
       Screen:
           name: 'screen1'
           BoxLayout:
               orientation: 'vertical'
               MDTopAppBar:
                   title: 'Home - Order List'
               ScrollView:
                   BoxLayout:
                       id: order_list
                       orientation: 'vertical'
                       size_hint_y: None
                       height: self.minimum_height
       Screen:
           name: 'screen2'
           BoxLayout:
               orientation: 'vertical'
               MDTopAppBar:
                   id: order_toolbar
                   title: 'Order Details'
               ScrollView:
                   GridLayout:
                       id: order_details
                       cols: 1
                       size_hint_y: None
                       height: self.minimum_height
   ```

## Usage

1. **Run the app:**

   ```sh
   python <app_script_name>.py
   ```

2. **Navigate through the app:**

   - The main screen (`screen1`) displays a list of orders.
   - Clicking on an order navigates to the details screen (`screen2`), where you can view and input purchase prices.
   - Calculate profit and mark orders as fulfilled using the provided buttons.

## Code Explanation

### Main Components

- **Fetching Orders:**

  The `get_all_orders` method connects to the Shopify API and retrieves all orders, storing their details in a dictionary.

- **Displaying Orders:**

  The main screen (`screen1`) displays a list of orders using `OneLineAvatarIconListItem`. Clicking an order item navigates to the details screen (`screen2`).

- **Calculating Profit:**

  On the details screen, users can input the purchase prices for each product. The `get_price` method calculates the total profit and updates the UI.

- **Fulfilling Orders:**

  The `fullfull_order` method marks an order as paid and fulfilled on the Shopify dashboard.

- **Database Interaction:**

  The `insert_record` method inserts or updates order records in a MySQL database.

### Threading

To ensure a smooth UI experience, database operations and API calls are handled in separate threads.


