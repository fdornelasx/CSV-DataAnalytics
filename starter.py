#-*- coding: utf8 -*-
import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

# Initialize the Flask application
app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = set(['csv'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def index():
    return render_template('index.html')


# Route that will process the file upload
@app.route('/upload', methods=['POST'])
def upload():
    # Get the name of the uploaded file
    file = request.files['file']
    # Check if the file is one of the allowed types/extensions
    if file and allowed_file(file.filename):
        # Make the filename safe, remove unsupported chars
        filename = secure_filename(file.filename)
        # Move the file form the temporal folder to
        # the upload folder we setup
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Redirect the user to the uploaded_file route, which
        # will basicaly show on the browser the uploaded file
        return redirect(url_for('uploaded_file',
                                filename=filename))

#Esta função abre um arquivo CSV, monta os dicionários e por fim a tabela no html
def prognoos(filename):
	import csv #lib pra trabalhar especificamente com csv
	#import datetime #lib para formatacao de datas, timestamps, etc...
	import time #lib para trabalhar com formatacao de data, delay, etc...
	n_assinaturas = 0 #numero total de assinaturas
	n_ativas = 0 #assinaturas ativas
	n_cancel = 0 #assinaturas canceladas
	stats = {} #dict que vai receber todas as variaveis de acima

	with open(filename) as csvfile: #abre um arquivo passado como parametro
		reader = csv.DictReader(csvfile) #abre esse arquivo especificamente como um csv
		for row in reader: #leitura de cada linha do arquivo
				
			data = time.strptime(row['payment_date'], "%Y-%m-%d %H:%M:%S") #formatacao do timestamp para identificação do ano,mes,dia
			key = str(data.tm_year)+"-"+str(data.tm_mon) #usando o ano e o mes para criar uma chave pro dict

			if key not in stats: #verifica se essa chave nao existe no dicionario
				stats[key] = {"n_assinaturas":0,"n_ativas":0,"n_cancel":0} #se nao existe, cria a chave e inicia com 0 todas as variaves

			if row["is_active"] == "1": #verifica se a assinatura ainda esta ativada
				stats[key]["n_ativas"]+=1 #se sim incrementa no valor de assinaturas ativas para aquela key
			else:
				stats[key]["n_cancel"]+=1 #se nao incrementa no valor de assinaturas canceladas

			stats[key]["n_assinaturas"]+=1 #incrementa sempre o numero total de assinatura para aquela key naquele mes

	return stats #retorna o dict montado para ser feita a tabela no html

@app.route('/uploads/<filename>')
def uploaded_file(filename):
	return render_template('sucesso.html',stats=prognoos(filename))
if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=int("8888")
    )
