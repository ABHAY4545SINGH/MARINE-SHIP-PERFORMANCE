from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.utils import secure_filename
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import bcrypt

app = Flask(__name__)
app.secret_key = 'supersecretmre'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)

    def __repr__(self):
        return f'<User {self.username}>'
    
    def __init__(self, username, password, email):
        self.username = username
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.email = email

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))  
    
with app.app_context():
    db.create_all()

df = pd.read_csv('Ship_Performance_Dataset.csv')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first() or User.query.filter_by(email=username).first()
        if not user:
            return jsonify({'message': 'User not found!'})
        if user and user.check_password(password):
            return jsonify({'message': 'Login successful!'})
        else:
            return jsonify({'message': 'Invalid username or password!'})
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({'message': 'Username already exists!'})
        new_user = User(username=username, password=password, email=email)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'Registration successful!'})
    return render_template('login.html')



#graph functions

# Operational Cost Vs Revenue

def operational_costvsrevenue():
    fig1 = px.scatter(
    df,
    x="Operational_Cost_USD",
    y="Revenue_per_Voyage_USD",
    color="Operational_Cost_USD",
    title="Operational Cost Vs Revenue",
    labels={"Operational Cost": "Operational Cost", "Revenue": "Revenue"},
    color_continuous_scale="Viridis",
)
    graph1_html = pio.to_html(fig1, full_html=False)
    return graph1_html
    
def average_operational_cost():
               avg_operational_cost = df.groupby('Ship_Type')['Operational_Cost_USD'].mean().reset_index()

               fig = px.bar(avg_operational_cost, x='Ship_Type', y='Operational_Cost_USD',
               title='Average Operational Cost by Ship Type',
               labels={'Operational_Cost_USD': 'Average Operational Cost (USD)', 'Ship Type': 'Ship Type'},
               color='Operational_Cost_USD', color_continuous_scale='Blues')

               graph2_html = pio.to_html(fig, full_html=False)
               return graph2_html

def route_type_vs_cost_revenue():
     grouped_data = df.groupby('Route_Type')[['Operational_Cost_USD','Revenue_per_Voyage_USD']].mean().reset_index()

     melted_data = grouped_data.melt(id_vars='Route_Type', value_vars=['Operational_Cost_USD', 'Revenue_per_Voyage_USD'],
                                var_name='Cost/Revenue Type', value_name='Value')

     fig = px.bar(melted_data, x='Route_Type', y='Value', color='Cost/Revenue Type',
                title='Average Operational Cost and Revenue by Route Type',
                labels={'Value': 'Average Value (USD)', 'Route_Type': 'Route Type'})
     
     graph3_html = pio.to_html(fig, full_html=False)
     return graph3_html

def cost_distribution_per_engine_type():
     fig = px.box(df, x='Engine_Type', y='Operational_Cost_USD', color='Engine_Type',
               title='Operational Cost Distribution by Engine Type',
               labels={'Operational_Cost_USD': 'Operational Cost (USD)', 'Engine_Type': 'Engine Type'})

     graph4_html = pio.to_html(fig, full_html=False)
     return graph4_html

# Efficiency analysis

def average_efficiency_ship_type():
    avg_efficiency = df.groupby('Ship_Type')['Efficiency_nm_per_kWh'].mean().reset_index()
    fig = px.bar(
    avg_efficiency, x='Ship_Type', y='Efficiency_nm_per_kWh',
    title='Average Efficiency by Ship Type',
    labels={'efficiency': 'Average Efficiency', 'Ship Type': 'Ship Type'},
    color='Efficiency_nm_per_kWh',
    color_continuous_scale='Viridis')

    graph5_html = pio.to_html(fig, full_html=False)
    return graph5_html

def efficiency_vs_distance_traveled():
    avg_efficiency = df.groupby('Ship_Type')['Efficiency_nm_per_kWh'].mean().reset_index()
    data_sorted = df.sort_values(by='Distance_Traveled_nm')

    fig = px.line(
    data_sorted,
    x='Distance_Traveled_nm',
    y='Efficiency_nm_per_kWh',
    title='Efficiency vs Distance Traveled',
    markers=True,
    labels={'Distance_Traveled_nm': 'Distance Traveled (nm)', 'Efficiency_nm_per_kWh': 'Efficiency (nm/kWh)'},   
)
    
    graph6_html = pio.to_html(fig, full_html=False)
    return graph6_html

def speed_vs_efficiency():
    avg_efficiency = df.groupby('Ship_Type')['Efficiency_nm_per_kWh'].mean().reset_index()

    fig = px.scatter(
    df,
    x='Speed_Over_Ground_knots',
    y='Efficiency_nm_per_kWh',
    color='Ship_Type',
    title='Speed vs Efficiency',
    labels={'Speed_knots': 'Speed (knots)', 'Efficiency_nm_per_kWh': 'Efficiency (nm/kWh)'},
    color_continuous_scale='turbo'
)
    
    graph7_html = pio.to_html(fig, full_html=False)
    return graph7_html

def Efficiency_vs_weather_and_maintenance():
    avg_efficiency = df.groupby('Ship_Type')['Efficiency_nm_per_kWh'].mean().reset_index()

    fig = px.density_heatmap(df, x='Weather_Condition', y='Maintenance_Status', z='Efficiency_nm_per_kWh',
                            color_continuous_scale='Viridis', title='Efficiency vs Weather & Maintenance')

    fig.update_layout(xaxis_title='Weather Condition', yaxis_title='Maintenance Status')

    graph8_html = pio.to_html(fig, full_html=False)
    return graph8_html

# overview dashboard

def ship_type_distribution():
     ship_counts = df['Ship_Type'].value_counts().reset_index()
     ship_counts.columns = ['Ship_Type', 'Count']

     fig = px.pie(ship_counts, values='Count', names='Ship_Type', title='Ship Type Distribution',
            color_discrete_sequence=px.colors.qualitative.Set3)
     
     graph9_html = pio.to_html(fig, full_html=False)
     return graph9_html

def Route_type_distribution():
    route_counts = df['Route_Type'].value_counts().reset_index()
    route_counts.columns = ['Route_Type', 'Count']

    fig = px.bar(route_counts, x='Route_Type', y='Count', title='Route Type Distribution',
             labels={'Route_Type': 'Route Type', 'Count': 'Count'},
             color='Count',
                color_continuous_scale='Blues')
    
    graph10_html = pio.to_html(fig, full_html=False)
    return graph10_html

def Weekly_voyage_count_by_ship_type():
    data_sorted = df.sort_values(by='Weekly_Voyage_Count',)

    fig = px.line(
    data_sorted,
    x='Weekly_Voyage_Count',
    y='Ship_Type',
    title='Weekly Voyage Count by Ship Type',
    markers=True,       
    labels={'Weekly_Voyage_Count': 'Weekly Voyage Count', 'Ship_Type': 'Ship Type'},
)
    
    graph11_html = pio.to_html(fig, full_html=False)
    return graph11_html


# maintenance and weather analysis

def maintenancce_status_vs_average_speed_cost():
    avg_data = df.groupby(['Maintenance_Status']).agg({'Speed_Over_Ground_knots': 'mean', 'Operational_Cost_USD': 'mean'}).reset_index()
    melted_data = avg_data.melt(id_vars='Maintenance_Status', value_vars=['Speed_Over_Ground_knots', 'Operational_Cost_USD'],
                            var_name='Metric', value_name='Value')
    fig = px.bar(
    melted_data,
    x='Maintenance_Status',
    y='Value',
    color='Metric',
    barmode='group',
    title='M gaintenance Status vs Average Speed and Operational Cost',
    labels={'Value': 'Average Value', 'Maintenance Status': 'Maintenance Status', 'Metric': 'Metric'},
    color_discrete_sequence=px.colors.qualitative.Set2
)

    graph12_html = pio.to_html(fig, full_html=False)
    return graph12_html


def weather_conditions_vs_efficiency():
    avgerage_efficiency = df.groupby('Weather_Condition')['Efficiency_nm_per_kWh'].mean().reset_index()

    fig = px.bar(
    avgerage_efficiency,
    x='Weather_Condition',
    y='Efficiency_nm_per_kWh',
    title='Average Efficiency by Weather Condition',
    labels={'Efficiency': 'Average Efficiency', 'Weather Condition': 'Weather Condition'},
    color='Efficiency_nm_per_kWh',
    color_continuous_scale='Sunset'
)
    
    graph13_html = pio.to_html(fig, full_html=False)
    return graph13_html

def speed_under_different_weather_conditions():
    fig = px.box(
    df,
    x='Weather_Condition',
    y='Speed_Over_Ground_knots',
    title='Speed Distribution under Different Weather Conditions',
    labels={'Weather Condition': 'Weather Condition', 'Speed': 'Speed'},
    color='Weather_Condition',
    color_discrete_sequence=px.colors.qualitative.Pastel
)
    
    graph14_html = pio.to_html(fig, full_html=False)    
    return graph14_html


def Cost_vs_Maintenance_Weather():
    avg_efficiency = df.groupby('Ship_Type')['Efficiency_nm_per_kWh'].mean().reset_index()

    grouped_data = df.groupby(['Maintenance_Status', 'Weather_Condition'])[['Operational_Cost_USD']].mean().reset_index()
    fig = px.density_heatmap(
    grouped_data,
    x='Maintenance_Status',
    y='Weather_Condition',
    z='Operational_Cost_USD',
    color_continuous_scale='Inferno',
    title='Heatmap of Operational Cost vs Maintenance and Weather',
    labels={'Operational Cost': 'Avg Operational Cost', 'Maintenance Status': 'Maintenance Status', 'Weather Condition': 'Weather Condition'}
)
    graph15_html = pio.to_html(fig, full_html=False)
    return graph15_html

# Speed and engine analysis

def Speed_over_ground_vs_distance_travelled():
    data_sorted = df.sort_values(by='Distance_Traveled_nm')

    fig = px.line(
    data_sorted, 
    x='Distance_Traveled_nm', 
    y='Speed_Over_Ground_knots', 
    title='Speed over Ground vs Distance Travelled',
    markers=True,
    labels={'Distance_Traveled_nm': 'Distance Travelled (nm)', 'Speed_over_Ground_knot': 'Speed over Ground (knot)'}
)
    graph16_html = pio.to_html(fig, full_html=False)
    return graph16_html


def engine_type_vs_average_speed():
    avg_speed = df.groupby('Engine_Type')['Speed_Over_Ground_knots'].mean().reset_index()
    fig = px.bar(
    avg_speed, 
    x='Engine_Type', 
    y='Speed_Over_Ground_knots', 
    title='Average Speed by Engine Type',
    labels={'Engine_Type': 'Engine Type', 'Speed_Over_Ground_knots': 'Average Speed (knot)'},
    color='Speed_Over_Ground_knots',
    color_continuous_scale='tealgrn'
)
    graph17_html = pio.to_html(fig, full_html=False)
    return graph17_html

def engine_power_vs_average_speed():
    average_speed_power = df.groupby('Engine_Power_kW')['Speed_Over_Ground_knots'].mean().reset_index()

    fig = px.scatter(
    average_speed_power, 
    x='Engine_Power_kW', 
    y='Speed_Over_Ground_knots', 
    title='Average Speed by Engine Power',
    labels={'Engine_Power_kW': 'Engine Power (kW)', 'Speed_Over_Ground_knots': 'Average Speed (knot)'},
    color='Speed_Over_Ground_knots',
    color_continuous_scale='viridis'
)
    
    graph18_html = pio.to_html(fig, full_html=False)
    return graph18_html

def speed_distribution():
    fig = px.histogram(
    df, 
    x='Speed_Over_Ground_knots', 
    nbins=30,
    title='Speed Distribution',
    labels={'Speed_Over_Ground_knots': 'Speed over Ground (knot)'},
    color_discrete_sequence=['skyblue']
)

    graph19_html = pio.to_html(fig, full_html=False)
    return graph19_html   





#analysis rotes

# Operational Cost Vs Revenue

@app.route('/Dashboard')
def Dashboard():
    graph9 = ship_type_distribution()
    graph10 = Route_type_distribution()
    graph11 = Weekly_voyage_count_by_ship_type()
    return render_template('Dashboard.html', graph9=graph9, graph10=graph10, graph11=graph11)

@app.route('/Efficiency_analysis')
def Efficiency_analysis():
    graph5 = average_efficiency_ship_type()
    graph6 = efficiency_vs_distance_traveled()
    graph7 = speed_vs_efficiency()
    graph8 = Efficiency_vs_weather_and_maintenance()
    return render_template('Efficiency_analysis.html', graph5=graph5, graph6=graph6, graph7=graph7, graph8=graph8)


@app.route('/maintenance_and_weather')
def maintenance_and_weather():
    graph12 = maintenancce_status_vs_average_speed_cost()
    graph13 = weather_conditions_vs_efficiency()
    graph14 = speed_under_different_weather_conditions()
    graph15 = Cost_vs_Maintenance_Weather()
    return render_template('maintenance_and_weather.html', graph12=graph12, graph13=graph13, graph14=graph14, graph15=graph15)
    

@app.route('/operational_cost')
def operational_cost():
    graph1 = operational_costvsrevenue()
    graph2 = average_operational_cost()
    graph3 = route_type_vs_cost_revenue()
    graph4 = cost_distribution_per_engine_type()
    return render_template('operational_cost.html', graph1=graph1, graph2=graph2, graph3=graph3, graph4=graph4)

@app.route('/speed_and_engine')
def speed_and_engine():
    graph16 = Speed_over_ground_vs_distance_travelled()
    graph17 = engine_type_vs_average_speed()
    graph18 = engine_power_vs_average_speed()
    graph19 = speed_distribution()
    return render_template('speed_and_engine.html', graph16=graph16, graph17=graph17, graph18=graph18, graph19=graph19)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)