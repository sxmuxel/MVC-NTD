from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

import os

# Inicializar la aplicación
app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave-secreta-para-mensajes-flash'

# Setup de SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar la base de datos
db = SQLAlchemy(app)

# Modelos
class Busqueda(db.Model):
    """Modelo para las búsquedas de cada integrante"""
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    base_datos = db.Column(db.String(50), nullable=False)
    cadena_busqueda = db.Column(db.String(300), nullable=False)
    cantidad_resultados = db.Column(db.Integer, nullable=False)
    fecha = db.Column(
        db.DateTime, 
        default=lambda: datetime.now(timezone(timedelta(hours=-5)))
    )

    articulos = db.relationship('Articulo', backref='busqueda', lazy=True)

class Articulo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(300), nullable=False)
    autores = db.Column(db.String(300), nullable=False)
    año = db.Column(db.Integer, nullable=False)
    revista = db.Column(db.String(200), nullable=False)
    resumen = db.Column(db.Text, nullable=False)
    palabras_clave = db.Column(db.String(300), nullable=False)
    referencia_apa = db.Column(db.Text, nullable=False)
    
    # Clave foránea
    busqueda_id = db.Column(db.Integer, db.ForeignKey('busqueda.id'), nullable=False)

class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=False)
    tipo_enfoque = db.Column(db.String(100), nullable=False, unique=False)
    descripcion = db.Column(db.Text)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

# Rutas
@app.route('/')
def index():
    """Página principal"""
    total_busquedas = Busqueda.query.count()
    total_articulos = Articulo.query.count()
    return render_template('index.html', 
                          total_busquedas=total_busquedas,
                          total_articulos=total_articulos)

@app.route('/busquedas')
def mostrar_busquedas():
    """Mostrar todas las búsquedas realizadas"""
    busquedas = Busqueda.query.all()
    return render_template('busquedas.html', busquedas=busquedas)

@app.route('/articulos')
def mostrar_articulos():
    """Mostrar todos los artículos"""
    articulos = Articulo.query.all()
    return render_template('articulos.html', articulos=articulos)

@app.route('/articulo/<int:id>')
def ver_articulo(id):
    """Ver un artículo específico"""
    articulo = Articulo.query.get_or_404(id)
    return render_template('crud/ver.html', articulo=articulo)

# Gestión de CRUDs
@app.route('/categorias')
def listar_categorias():
    """Listar todas las categorías"""
    categorias = Categoria.query.all()
    return render_template('crud/listar.html', categorias=categorias)

@app.route('/categoria/nueva', methods=['GET', 'POST'])
def crear_categoria():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        tipo_enfoque = request.form.get('tipo_enfoque')
        descripcion = request.form.get('descripcion')

        if not tipo_enfoque:
            flash('Debe seleccionar un tipo de enfoque', 'danger')
            return redirect(url_for('crear_categoria'))

        nueva_categoria = Categoria(
            nombre=nombre,
            tipo_enfoque=tipo_enfoque,
            descripcion=descripcion,
            fecha_creacion=datetime.now(timezone(timedelta(hours=-5)))
        )

        db.session.add(nueva_categoria)
        db.session.commit()

        flash('Categoría creada exitosamente!', 'success')
        return redirect(url_for('listar_categorias'))

    return render_template('crud/crear.html')

@app.route('/categoria/editar/<int:id>', methods=['GET', 'POST'])
def editar_categoria(id):
    """Editar categoría existente"""
    categoria = Categoria.query.get_or_404(id)
    
    if request.method == 'POST':
        categoria.nombre = request.form['nombre']
        categoria.tipo_enfoque = request.form['tipo_enfoque']
        categoria.descripcion = request.form['descripcion']
        
        db.session.commit()
        flash('Categoría actualizada exitosamente!', 'success')
        return redirect(url_for('listar_categorias'))
    
    return render_template('crud/editar.html', categoria=categoria)

@app.route('/categoria/eliminar/<int:id>')
def eliminar_categoria(id):
    """Eliminar categoría"""
    categoria = Categoria.query.get_or_404(id)
    db.session.delete(categoria)
    db.session.commit()
    
    flash('Categoría eliminada exitosamente!', 'danger')
    return redirect(url_for('listar_categorias'))

# Datos de Ejemplo
def crear_datos_ejemplo():
    if Busqueda.query.count() == 0:
        print("Creando datos de ejemplo...")
        
        # Creación de búsquedas
        busqueda1 = Busqueda(
            nombre="Steban Cadena",
            base_datos="Scopus",
            cadena_busqueda="“Artificial Intelligence” AND “Systems Engineering”",
            cantidad_resultados=10410
        )
        db.session.add(busqueda1)
        
        busqueda2 = Busqueda(
            nombre="Samuel Villalobos",
            base_datos="Scopus",
            cadena_busqueda = "( TITLE-ABS-KEY ( \"artificial intelligence\" OR \"AI\" OR \"machine learning\" OR \"deep learning\" ) ) AND ( TITLE-ABS-KEY ( \"systems engineering\" OR \"software engineering\" OR \"computer systems\" ) )",
            cantidad_resultados=19211
        )
        db.session.add(busqueda2)

        busqueda3 = Busqueda(
            nombre="Sebastian Campo",
            base_datos="Scopus",
            cadena_busqueda="TITLE-ABS-KEY ( decision-making  AND systems  OR  intelligent  AND information  AND systems ) ",
            cantidad_resultados=147930
        )
        db.session.add(busqueda3)        
        
        db.session.commit()
        
        # Creación de artículos relacionados a las búsquedas
        articulo1 = Articulo(
            titulo="Stabilizing truth in educational sciences: A systematic review of generative AI in education.",
            autores="Brezovec, E., Zelić, M., & Zagode, A. M.",
            año=2026,
            revista="Kybernetes, 1-19",
            resumen="This paper examines how the scientific system, particularly the educational sciences, observes and communicates the phenomenon of generative artificial intelligence (AI) in education. Drawing on Luhmann’s social systems theory, the purpose is to reconstruct how scientific communication stabilizes truth by framing AI through distinctions such as augmentation, automation, and hybrid models.",
            palabras_clave="social systems, education, artificial intelligence, system theory, autopoiesis",
            referencia_apa="Brezovec, E., Zelić, M., & Zagode, A. M. (2026). Stabilizing truth in educational sciences: A systematic review of generative AI in education. Kybernetes, 1-19. https://doi.org/10.1108/K-09-2025-2339",
            busqueda_id=1
        )
        db.session.add(articulo1)

        articulo2 = Articulo(
            titulo="Modality augmentation and task-aware dual-modal LoRAs for multi-task multimodal federated learning.",
            autores="Zeng, Y., Ren, H., Cai, Y., Li, Y., & Jing, Q.",
            año=2026,
            revista="Information Processing & Management, 63, Article 104601",
            resumen="Multimodal Federated Learning (MFL) is a decentralized machine learning paradigm designed to integrate knowledge from clients with diverse modalities into a global model without compromising privacy. Existing MFL methods suffer from two critical limitations: modality bias and task incompatibility. These two limitations stem from modality inconsistency and task heterogeneity among clients, which lead to degraded performance of the global server model on client-specific tasks. To tackle these problems, we introduce a multi-task compatible framework with a modality augmentation(MA) and a task-aware selective local feature aggregation (TA-SLFA). The designed MA and TA-SLFA modules respectively aim to tackle the modality bias and alleviate the task heterogeneity in MFL. Moreover, the task-aware dual-modal Low-Rank Adaptations (LoRAs) are integrated into a vision-language model, enhancing its ability to integrate task-specific features and improve multi-task learning ability. Extensive experiments and ablation analysis are conducted on four common public datasets and the experimental results demonstrate that our proposed model achieves significant improvements in multitask multimodal federated learning.",
            palabras_clave="multimodal federated learning, multi-task learning, vision-language models, low-rank adaptation, systems engineering, artificial intelligence",
            referencia_apa="Zeng, Y., Ren, H., Cai, Y., Li, Y., & Jing, Q. (2026). Modality augmentation and task-aware dual-modal LoRAs for multi-task multimodal federated learning. Information Processing & Management, 63, Article 104601. https://doi.org/10.1016/j.ipm.2025.104601",            
            busqueda_id=2
        )
        db.session.add(articulo2)    

        articulo3 = Articulo(
            titulo="Intelligent parameter recommendation for substation design using knowledge graph and graph neural networks ",
            autores="Zhou, Liang., Gao, Zhen-Ting., Zhai, Pen-Fan., Zeng, Yi-Heng.",
            año=2026,
            revista="Energy Informatics",
            resumen="As power systems move toward digitalization and low-carbon transformation, improving the intelligence of substation design processes has become increasingly critical. Traditional equipment parameter selection relies heavily on manual experience and fragmented document retrieval, leading to inefficiencies, inconsistencies, and limited scalability. This paper proposes an intelligent parameter recommendation method tailored for substation engineering, integrating domain-specific knowledge graphs with adaptive graph neural networks (GNNs). The framework first extracts structured equipment information from multi-voltage substation design drawings using entity disambiguation, then constructs a hierarchical knowledge graph to represent inter-device relationships. A natural language interface captures user queries and encodes them into context-aware instruction vectors. These are used to guide a hybrid reasoning process that combines fuzzy rule matching and GNN-based relation inference. Case studies using real-world 10 kV/110 kV substation projects demonstrate that the proposed method significantly outperforms existing knowledge graph-based baselines in both accuracy and interpretability. The results show that this work is superior to the comparison baseline model in both ACC and AUC indicators, and support intelligent decision-making throughout the equipment lifecycle. This work provides a scalable solution for knowledge-driven substation design automation in the era of smart grids.",
            palabras_clave="artificial intelligence, power systems, substation design, knowledge graphs, graph neural networks, intelligent automation",
            referencia_apa="Zhou, Liang., Gao, Zhen-Ting., Zhai, Pen-Fan., Zeng, Yi-Heng. (2026). Intelligent parameter recommendation for substation design using knowledge graph and graph neural networks. Energy Informatics. https://doi.org/10.1186/s42162-025-00605-6",
            busqueda_id=3
        )
        db.session.add(articulo3)            
        
        # Crear CRUDs de ejemplo
        cat1 = Categoria(nombre="ChatGPT en las Escuelas", tipo_enfoque= "Augmentation", descripcion="Asiste a estudiantes y docentes en la redacción de textos, resolución de dudas y apoyo al aprendizaje")
        cat2 = Categoria(nombre="Corrección Automática de Ensayos", tipo_enfoque= "Automation", descripcion="Sistema que evalúa ensayos académicos y asigna calificaciones automáticamente")
        cat3 = Categoria(nombre="Tutor Virtual Inteligente", tipo_enfoque= "Hybrid", descripcion="Combina asistencia al estudiante con evaluación automática del progreso")

        db.session.add_all([cat1, cat2, cat3])
        
        db.session.commit()
        print("Datos de ejemplo creados exitosamente!")

# Inicialización

if __name__ == '__main__':
    with app.app_context():
        # Crear todas las tablas si no existen
        db.create_all()
        crear_datos_ejemplo()
    
    print("\nEl servidor de Flask se ha iniciado ✅")
    print("Corriendo en: http://localhost:5000\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)