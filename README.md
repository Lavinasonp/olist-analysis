<div align="center">
  <img src="https://avatars.githubusercontent.com/u/27393444" alt="Olist Logo" width="150"/>
</div>

# Olist Supply Chain & Operations Analytics

This repository contains an end-to-end operational analytics dashboard designed to optimize logistics, reduce freight costs, and improve seller performance for Olist, the largest department store in Brazilian marketplaces.

## Business Context

Olist connects small businesses from all over Brazil to channels without hassle and with a single contract. Those merchants are able to sell their products through the Olist Store and ship them directly to the customers using Olist logistics partners. 

As the business scales, operational bottlenecks in the supply chain directly impact customer satisfaction and conversion rates. This project provides a deep dive into the transaction, logistics, and product rating data to extract actionable business strategies.

## Strategic Objectives

1. **Delivery Performance Optimization**
   Analyze carrier transit times versus seller processing times across all Brazilian states to identify regional bottlenecks and inform logistics partnerships.
   
2. **Freight Cost Reduction**
   Map freight costs as a percentage of the final product price to identify geographic zones where shipping acts as a deterrent to conversion, guiding dynamic pricing and shipping subsidy strategies.

3. **Seller Quality Management**
   Evaluate average seller dispatch times to create performance-based ranking algorithms and incentive structures.

4. **Product Quality & Customer Satisfaction**
   Correlate product categories with customer review scores to identify poor-performing verticals that require strict quality assurance interventions.

## Key Business Insights

Based on the data processed in this dashboard, several critical operational insights have been formulated:

- **Regional Logistics Disparities**: Northern and Northeastern states experience late delivery rates exceeding 15 percent, driven almost entirely by extended carrier transit times rather than seller delays. Diversifying the regional carrier portfolio is highly recommended.
- **Freight as a Conversion Barrier**: In remote states, shipping costs frequently exceed 30 percent of the product price. Implementing targeted freight subsidies for high-margin, lightweight categories can significantly boost regional sales.
- **Seller Dispatch Inconsistencies**: There is high variance in how quickly sellers hand over products to the carrier. Implementing a "Fast Dispatch" badge for sellers who ship within 48 hours is recommended to drive behavioral changes.
- **Payment Method Frictions**: A significant portion of transactions rely on Boletos, which delay the entire order lifecycle due to payment confirmation times. Incentivizing instant payments (like PIX or Credit Card) via small discounts can streamline operations.

## Technologies Used

<div align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white" alt="Pandas"/>
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit"/>
  <img src="https://img.shields.io/badge/Plotly-239120?style=for-the-badge&logo=plotly&logoColor=white" alt="Plotly"/>
</div>
