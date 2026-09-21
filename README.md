# 🌾 PestRisk AI

## Multi-Pest Weather-Based Risk Prediction and Sustainable IPM Advisory for Rice

PestRisk AI is an AI-powered decision-support system for rice pest management. It combines **Machine Learning-based pest observation risk prediction**, **Retrieval-Augmented Generation (RAG)**, and **LLM-based advisory generation** to provide pest-specific and sustainable Integrated Pest Management (IPM) guidance.

The system uses weather, seasonal, location, and selected pest information to estimate the probability of observing the selected pest under the given conditions. The predicted probability is then classified into Low, Medium, or High risk and combined with retrieved agricultural knowledge to generate a farmer-friendly advisory.

> **Note:** PestRisk AI predicts the risk of observing a selected pest in the surveillance context. It does not directly measure field infestation, crop loss, yield improvement, or pesticide reduction.

---

## 🚀 Live Demo

🌐 **Streamlit Application:**  
https://pestrisk-ai-gtvarbmjupfnpbgrr7aeeb.streamlit.app/

💻 **GitHub Repository:**  
https://github.com/Lakshmi-TU/PestRisk-AI

---

## 🎯 Problem Statement

Rice production can be affected by multiple pests whose occurrence varies with environmental and seasonal conditions.

Farmers and agricultural practitioners need timely information about:

- Which pest is relevant under the current conditions
- The predicted observation risk
- Pest symptoms and identification
- What should be monitored
- Sustainable pest-management practices
- Integrated Pest Management (IPM) approaches

Agricultural pest-management information is often distributed across different sources. PestRisk AI brings prediction and pest-management knowledge together in a single AI-assisted decision-support system.

---

## 💡 Proposed Solution

PestRisk AI follows a multi-stage pipeline:

```text
Weather + Time + Location + Selected Pest
                    ↓
             Machine Learning
             Risk Prediction
                    ↓
        Pest Observation Probability
                    ↓
          Low / Medium / High Risk
                    ↓
            RAG Knowledge Base
                    ↓
       Pest-Specific IPM Information
                    ↓
             LLM Advisory
                    ↓
        Sustainable Farmer Guidance
