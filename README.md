# 🚦 Traffic Signal Optimization

### An Interactive Traffic Analysis and Signal Optimization Dashboard

## 📌 About the Project

This project presents an interactive, simulation-based framework for analysing traffic conditions across selected intersections in Ahmedabad and exploring traffic signal optimization under varying traffic demand conditions.

Developed using Python and Streamlit, the dashboard combines statistical analysis, vehicle composition modelling, future traffic scenario simulation, and mathematical optimization to understand traffic patterns and evaluate alternative signal timing strategies.

The project focuses on analysing current traffic conditions (2026) and exploring possible future traffic conditions (2036) under different growth and vehicle composition assumptions.

## 🎯 Key Features

- **Traffic Overview:** Interactive overview of traffic conditions and key performance indicators across selected intersections.
- **Current Traffic Analysis (2026):** Examination of vehicle volume, average speed, queue length, waiting time, and vehicle arrival rates.
- **Statistical Analysis:** Analysis of traffic patterns across intersections, approaches, and time bands using descriptive statistics and hypothesis testing.
- **Vehicle Composition Analysis:** Examination of the distribution of two-wheelers, cars, auto-rickshaws, buses, and other vehicle categories.
- **Future Scenario Modelling (2036):** Simulation of Low, Moderate, and High traffic growth scenarios.
- **Vehicle Composition Scenarios:** Exploration of alternative traffic mixes, including Current Composition, More Two Wheelers, and More Cars.
- **Comparative Analysis:** Comparison of current traffic conditions with simulated future scenarios to understand the potential impact of changing traffic demand and vehicle composition.
- **Traffic Flow Pulse:** Interactive visualization of traffic pressure and vehicle composition across selected intersections.
- **Signal Timing Optimization:** Mathematical optimization of green signal time allocation between North–South and East–West traffic movements.

## 📊 Analysis and Methodology

The project follows a structured analytical approach:

1. **Exploratory Data Analysis:** Examined traffic data using descriptive statistics, distribution analysis, and comparisons across intersections, approaches, and time bands.
2. **Statistical Testing:** Applied normality assessment and paired t-tests to examine differences in traffic demand between North–South and East–West approaches.
3. **Vehicle Composition Analysis:** Studied the contribution of different vehicle categories to overall traffic demand.
4. **Scenario-Based Simulation:** Developed alternative 2036 traffic scenarios by varying traffic growth assumptions and vehicle composition.
5. **Mathematical Optimization:** Evaluated signal timing allocations to identify a suitable distribution of green time between the two traffic movements under the selected objective formulation.

## 📈 Key Findings and Outcomes

- Identified variations in vehicle arrival rates and traffic demand across intersections, time bands, and approaches.
- Observed higher average arrival rates for the North–South approach compared with the East–West approach in the analysed dataset, supported by statistical testing.
- Examined how different traffic growth assumptions and vehicle composition changes influence simulated future traffic conditions.
- Developed interactive comparisons between current traffic conditions and multiple future scenarios for 2036.
- Obtained an optimized signal allocation of approximately **56.41 seconds for North–South** and **53.59 seconds for East–West** under the selected optimization setup.
- Achieved a small improvement over the existing 55–55 second allocation in the selected scenario, demonstrating the application of mathematical modelling to traffic signal timing decisions.

## 🛠️ Technologies Used

- **Programming Language:** Python
- **Data Analysis:** Pandas, NumPy
- **Visualization:** Plotly
- **Dashboard Development:** Streamlit
- **Scientific Computing and Optimization:** SciPy
- **Interface Design:** HTML, CSS

## 🔍 Analytical Approach

The project primarily uses statistical and mathematical techniques, including:

- Descriptive Statistical Analysis
- Distribution and Normality Analysis
- Hypothesis Testing
- Comparative and Sensitivity Analysis
- Scenario-Based Simulation
- Mathematical Optimization

*The framework is simulation-based and does not rely on machine learning or deep learning models.*

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/itsaainaa/Traffic-Signal-Optimization.git
```

### 2. Navigate to the Project Directory

```bash
cd Traffic-Signal-Optimization
```

### 3. Install Dependencies

```bash
pip install streamlit pandas numpy plotly scipy
```

### 4. Run the Dashboard

```bash
python -m streamlit run app.py
```

The dashboard will be available at:

```text
http://localhost:8501
```

## 📁 Project Structure

```text
Traffic-Signal-Optimization/
│
├── app.py
├── Ahmedabad_Traffic_2036_Master_Dataset.csv
├── requirements.txt
└── README.md
```

## 🔮 Future Scope

- Incorporating real-time traffic data for more dynamic analysis.
- Exploring additional traffic growth and vehicle composition scenarios.
- Extending the optimization framework to multiple intersections and signal phases.
- Evaluating alternative optimization objectives and constraints.

## 🎓 Project Focus

This project demonstrates the application of **mathematics, statistics, data analysis, simulation, and optimization** to an urban traffic management problem.

It aims to show how analytical methods can help understand traffic behaviour, explore future demand conditions, and support more informed traffic signal timing decisions.

---

**Developed with Python | Statistical Analysis | Mathematical Modelling | Traffic Optimization**
