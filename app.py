# Import the necessary packages.
import requests
from flask import Flask, request, render_template, redirect, url_for

from models.CAeropuerto import CAeropuerto

#Creamos los datos para inicializar la app
aiportEntity = CAeropuerto()
listAriports = aiportEntity.listNodos
listAirportsAvoided = []

# Create a Flask app.
app = Flask(__name__)

# Define a route that accepts two airport codes as input and returns the minimum cost flight cost between them.
@app.route("/", methods=["GET"])
def get_flight_cost():
    return redirect(url_for('initCalcRoute'))

@app.route("/initCalcRoute")
def initCalcRoute():
    return render_template('calcRoute.html', airports = listAriports)

@app.route("/initDeleteRoute")
def initDeleteRoute():
    return render_template('deleteRoute.html', airports = listAriports)
@app.route("/initTechnicalView")
def initTechnicalView():
    return render_template('technicalView.html', airports = listAriports)

@app.route("/showMapa", methods = ["POST"])
def showMapa():
    origen = request.form['origen']
    destino = request.form['destino']
    mapa, costoTotal = aiportEntity.getMapaResult(origen, destino, listAirportsAvoided)
    track = f"{origen} - {destino}"
    if(costoTotal == 0 ):
        htmlMap = False
    else:
        htmlMap = mapa._repr_html_()
    #htmlMap = mapa.get_root().render()
    #mapaRender = render_template('calcRoute.html', map = htmlMap)
    #mapa.save('templates/mapa.html')
    return render_template('calcRoute.html', map = htmlMap, airports = listAriports, costoTotal = costoTotal, track = track)

@app.route("/showTechnicalView", methods = ["POST"])
def showTechnicalView():
    origen = request.form['origen']
    destino = request.form['destino']
    urlimg = aiportEntity.get_graph(origen, destino, listAirportsAvoided)
    return render_template('technicalView.html', airports = listAriports, urlimg = urlimg)

@app.route("/deleteRuta", methods = ['POST'])
def deleteAirport():
    airport = request.form['airport']
    if(airport not in listAirportsAvoided):
        listAirportsAvoided.append(airport)
        return render_template('/deleteRoute.html', message = True, airports = listAriports, airport = airport)
    else:
        return render_template('/deleteRoute.html', message = False, airports = listAriports, airport = airport)

@app.route("/showCompleteMap")
def showCompleteMap():

    return render_template('mapaComplete.html')


# Run the Flask app.
if __name__ == "__main__":
    app.run(debug=True)
