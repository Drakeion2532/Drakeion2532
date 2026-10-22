# Hi, I'm Shubhan Punde

**Data science for credit and fraud risk.** I'm a Computer Engineering graduate from VIT Pune (2026). I spent a year in risk detection at RNS Technology, first as an intern and then as a full-time analyst.

I build models that end in a decision someone can act on: an alert queue, an approve/decline call, a step-up MFA prompt. They don't stop at a score.

📍 Pune, willing to relocate · ✉️ shubhanpunde@gmail.com · [LinkedIn](https://linkedin.com/in/shubhan-punde-56378b222)

---

### Featured: credit & fraud risk

| Project | What it does | Key result |
|---|---|---|
| [**Card Fraud Analytics at Scale**](https://github.com/Drakeion2532/card-fraud-analytics-spark)<br><sub>PySpark · Spark SQL · Hive · MLlib</sub> | Spark pipeline on 10M simulated card transactions. Hive tables are partitioned by day, and velocity attributes come from SQL window functions. The output is a daily review queue ranked by risk, with a reason for each alert. | At the same 0.34% alert rate, the model catches **82% of fraud** (87% of value); rules catch 47%. |
| [**Credit Default Scorecard**](https://github.com/Drakeion2532/credit-default-scorecard)<br><sub>Python · scikit-learn · Logistic Regression</sub> | Logistic scorecard on 1,000 loan applicants. A decision tool returns approve/decline with plain-language reasons. | **0.60 Gini**, 0.48 KS on held-out data. The expected-loss cut-off catches 91% of defaults at 34% lower cost. |
| [**Identity Risk Engine**](https://github.com/Drakeion2532/identity-risk-engine)<br><sub>Python · Isolation Forest · FastAPI</sub> | Account-takeover detection on Okta System Log events. Each login is scored against that user's own baseline and gets one of three decisions: allow, step-up MFA, or block. | Caught **all 74 attacks** in 7 scenarios (0.976 PR-AUC), with ~10× fewer false alerts than Isolation Forest alone. |
| [**PhishGuard**](https://github.com/Drakeion2532/phishing-url-detector)<br><sub>XGBoost · FastAPI · Chrome extension</sub> | Phishing and scam detector that checks URLs and whole SMS/WhatsApp messages, including OTP scams with no link. | **97.4% accuracy** and 1.9% false positives on 120K URLs. 87.9% recall on an unseen phishing feed. |

### Other work

- [**COVID-19 forecasting**](https://github.com/Drakeion2532/covid19-time-series-forecasting) (UNLV research internship): 30-day forecasts for 6 countries. The ensemble cut normalized RMSE by 25% against a naive baseline.
- [**Explainable intrusion detection**](https://github.com/Drakeion2532/network-intrusion-detection): turns a batch of flagged network flows into a ranked incident list, with SHAP reasons for each.
- [**Real-time traffic management**](https://github.com/Drakeion2532/Traffic-Management-using-Deep-Learning): YOLOv8 vehicle detection drives demand-based signal timing (IEEE paper).
- [**Doctor Sahyog / Patient Mitra**](https://github.com/Drakeion2532/doctor-sahyog-health-card): QR health card with an audit trail and FHIR R4 export (published paper).
- [**Plant disease CNN**](https://github.com/Drakeion2532/plant-disease-detection-cnn) · [**Smart Kitchen IoT**](https://github.com/Drakeion2532/smart-kitchen-iot)

### Publications

- [Multi-Model Ensemble Approach for Enhanced Cyberbullying Detection Across Diverse Categories](https://ieeexplore.ieee.org/document/10823191). IEEE Xplore (ICICNIS 2024)
- [Real-Time Traffic Management Using Deep Learning and Object Detection using YOLOv8](https://ieeexplore.ieee.org/document/10725412). IEEE Xplore (ICCCNT 2024)
- [Patient Mitra: Health Card](https://openurl.ebsco.com/EPDB%3Agcd%3A3%3A2283619/detailv2?sid=ebsco%3Aocu%3Arecord&id=ebsco%3Agcd%3A171360364&bquery=IS%202395-5287%20AND%20VI%209%20AND%20IP%202%20AND%20DT%202023&page=1). GIJET 2023

### Toolkit

**Data & big data:** Python, SQL, R, PySpark, Spark SQL, Hive, Spark MLlib, Pandas, Parquet<br>
**Modelling:** Logistic Regression, Decision Trees, Gradient Boosting, XGBoost, Isolation Forest, PyTorch, time-series forecasting<br>
**Risk:** credit scorecards (Gini, KS), fraud & account-takeover detection, cost-based cut-offs, SHAP reason codes<br>
**Engineering:** FastAPI, pytest, GitHub Actions, Git, Linux, Power BI

**Certifications:** [IBM Data Warehouse Engineer](https://www.coursera.org/account/accomplishments/specialization/E5PB8YR2VWKP) · Data Analyst Course (GeeksforGeeks) · Querying Databases with SQL · [Saviynt ISAA](https://certification.saviynt.com/961c5f95-ccc1-4138-a715-f018e287609d#acc.ueJPXyiW)
