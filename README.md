# 🚀 Automated Data Profiling for Regulatory Reporting  

## 📌 Table of Contents  
- [Introduction](#-introduction)  
- [Demo](#-demo)  
- [Inspiration](#-inspiration)  
- [What It Does](#-what-it-does)  
- [How We Built It](#-how-we-built-it)  
- [Challenges We Faced](#-challenges-we-faced)  
- [How to Run](#-how-to-run)  
- [Tech Stack](#-tech-stack)  
- [Team](#-team)  

📄 **Federal Reserve Rules Reference**: [Download Here](https://www.federalreserve.gov/apps/reportingforms/Download/DownloadAttachment?guid=83c6e71a-86c2-40b6-a9a5-16e15ca7d2d8)  

---

## 🎯 Introduction  
Automated Data Profiling for Regulatory Reporting is a system that uses **Generative AI (LLMs) and Unsupervised Machine Learning techniques** to extract validation rules, detect anomalies, generate validation code, and provide flagged transactions with reasons. This helps financial institutions ensure compliance with federal regulations while reducing manual effort.  

---

## 🎥 Demo  
📹 [Video Demo](https://drive.google.com/file/d/1E4YUHqEBMp4MVgqeY1aFmDyGEPbSDhhd/view?usp=sharing) 
🖼️ Screenshots:  
![Screenshot 1](link-to-image)  

---

## 💡 Inspiration  
Regulatory compliance is a **critical challenge** in the financial sector, requiring **accurate and efficient data validation**. Manually profiling large datasets for anomalies and rule violations is time-consuming. This project **automates the process** using **AI-driven rule extraction** and **anomaly detection**, improving efficiency and accuracy.  

---

## ⚙️ What It Does  
🔍 **Extracts validation rules** from financial data  
🚨 **Detects anomalies** in transactional records  
📝 **Generates validation code** automatically  
📊 **Flags suspicious transactions** with detailed reasoning  
📎 **Outputs results in a structured CSV format**  

---

## 🛠️ How We Built It  
- **Data Collection & Profiling**: Used sample **transaction datasets** to create validation rules  
- **Generative AI & LLMs**: Extracted regulatory rules and **automated validation logic generation**  
- **Unsupervised ML**: Identified **anomalies and suspicious patterns** in transactions  
- **Automation Pipeline**: Integrated **rule extraction, anomaly detection, and reporting**  

---

## 🚧 Challenges We Faced  
⚠️ **Handling complex regulatory rules** and converting them into machine-readable formats  
📊 **Optimizing anomaly detection** without excessive false positives  
💾 **Processing large financial datasets** efficiently  
🛠️ **Ensuring model interpretability** for audit and compliance teams  

---


## 🏃 How to Run  
1. Clone the repository  
   ```sh
   git clone https://github.com/ewfx/gaidp-ranga.git

2. Install dependencies  
   ```sh
   pip install -r requirements.txt  

   ```
3. Run the project  
   ```sh
   streamlit run code/src/app_interface.py
   ```

## 🏗️ Tech Stack
- 🔹 Frontend: Streamlit
- 🔹 Backend: Python
- 🔹 Machine Learning: OpenAI API (LLMs), Scikit-learn, Pandas, numpy
- 🔹 Other: Google Generative AI, PyMuPDF


## 👥 Team-RANGA
- **Gautam Singh** - [GitHub](https://github.com/gautamdevloper) | [LinkedIn](https://www.linkedin.com/in/gautam-singh-1707/)
- **Rahul Priyadarshi** - [GitHub](https://github.com/rahulp99) | [LinkedIn](https://www.linkedin.com/in/rahul-pr99/)
- **Akshaj Sunil** - [GitHub](https://github.com/akshajsunil) | [LinkedIn](https://www.linkedin.com/in/akshaj-sunil-ba219a179/)
- **Arjun Bindu Jayachandran** - [GitHub](https://github.com/Arjun-B-J) | [LinkedIn](https://www.linkedin.com/in/arjun-bindu-jayachandran-76741a185/)
- **Naveen Kumar Vunnam** - [GitHub](https://www.linkedin.com/in/naveen-kumar-vunnam-9a064b177) | [LinkedIn](https://www.linkedin.com/in/naveen-kumar-vunnam-9a064b177/)
