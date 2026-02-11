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
            cadena_busqueda = 'TITLE-ABS-KEY ( "artificial intelligence" ) AND TITLE-ABS-KEY ( "systems engineering" ) ) AND ( LIMIT-TO ( OA , "all" )',
            cantidad_resultados=10410
        )
        db.session.add(busqueda1)
        
        busqueda2 = Busqueda(
            nombre="Samuel Villalobos",
            base_datos="Scopus",
            cadena_busqueda = 'TITLE-ABS-KEY ( "artificial intelligence" OR "AI" OR "machine learning" OR "deep learning" ) AND TITLE-ABS-KEY ( "systems engineering" OR "software engineering" OR "computer systems" )',
            cantidad_resultados=19211
        )
        db.session.add(busqueda2)

        busqueda3 = Busqueda(
            nombre="Sebastian Campo",
            base_datos="Scopus",
            cadena_busqueda = 'TITLE-ABS-KEY ( "decision-making" AND "systems" OR "intelligent" AND "information" AND "systems" )',
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
            titulo="Research on the refinement of college student education management based on artificial intelligence.",
            autores="Lai, Qiujia.",
            año=2026,
            revista="Discover Artificial Intelligence, 6, Article 31",
            resumen="In the era of digital transformation, traditional college student education (CSE) management faces several challenges, including inefficiency, a lack of personalization, and delayed decision-making. To address these limitations, this research aims to integrate artificial intelligence (AI) into education management systems, aiming to refine and enhance both administrative and academic processes in higher education institutions. AI technologies provide significant potential to improve various facets of student management, such as academic performance monitoring, behavioral analysis, early risk detection, and personalized learning support. The dataset used in the research comprises academic records, including course grades, attendance logs, and enrollment histories. Additionally, behavioral and engagement metrics were collected from institutional learning management systems. To prepare the data for model training, feature normalization was performed using the Min-Max scaling technique, and principal component analysis (PCA) was employed for feature extraction. This research proposes a novel deep learning-based Artificial Gorilla Troops Optimizer-driven Residual Recurrent Neural Network (AGTO-ResRNN) model to automate student profiling and intervention planning. The model enables proactive academic advising and timely delivery of personalized support services by adjusting educational strategies based on predictive insights. The experimental implementation of the AGTO-ResRNN model demonstrated significant improvements in education management accuracy, operational efficiency, and student satisfaction. Key performance indicators, such as MAE (0.116), accuracy (98.50%), recall (95.42%), RMSE (0.183), F1-score (96.00%), and precision (96.54%), showed substantial enhancement compared to traditional methods. The research suggests that AI-driven management systems can enhance the educational environment, providing valuable insights to modernize student support.",
            palabras_clave="artificial intelligence, education management systems, higher education, student performance analytics, deep learning, intelligent decision support systems",
            referencia_apa="Lai, Qiujia. Research on the refinement of college student education management based on artificial intelligence. Discover Artificial Intelligence, 2026. DOI: https://doi.org/10.1007/s44163-025-00651-9",
            busqueda_id=1
        )
        db.session.add(articulo2)  

        articulo3 = Articulo(
            titulo="Robotics and artificial intelligence applications in neurorehabilitation: a bibliometric analysis (2003–2025).",
            autores="Taskaya, B., & Taskaya, C.",
            año=2026,
            revista="Journal of NeuroEngineering and Rehabilitation, 23, Article 55",
            resumen="Robotic and artificial intelligence (AI)-assisted neurorehabilitation has emerged as a rapidly growing interdisciplinary field, integrating engineering innovations with clinical practice to enhance motor and cognitive recovery in neurological disorders. While research in this domain has expanded substantially over the last two decades, only a few bibliometric studies have examined related topics (e.g., new technologies in neurorehabilitation, rehabilitation robotics after stroke, AI in stroke care), and, to our knowledge, no study has provided a comprehensive bibliometric mapping specifically focused on robotics and artificial intelligence applications in neurorehabilitation. This study aimed to analyse the global trends, influential contributors, thematic evolution, and collaborative networks in robotic and AI-assisted neurorehabilitation.",
            palabras_clave="robotics, artificial intelligence, neurorehabilitation, rehabilitation engineering, bibliometric analysis, intelligent healthcare systems",
            referencia_apa="Taskaya, B., & Taskaya, C. (2026). Robotics and artificial intelligence applications in neurorehabilitation: a bibliometric analysis (2003–2025). Journal of NeuroEngineering and Rehabilitation, 2026. https://doi.org/10.1186/s12984-025-01870-y",
            busqueda_id=1
        )
        db.session.add(articulo3)              

        articulo4 = Articulo(
            titulo="Modality augmentation and task-aware dual-modal LoRAs for multi-task multimodal federated learning.",
            autores="Zeng, Y., Ren, H., Cai, Y., Li, Y., & Jing, Q.",
            año=2026,
            revista="Information Processing & Management, 63, Article 104601",
            resumen="Multimodal Federated Learning (MFL) is a decentralized machine learning paradigm designed to integrate knowledge from clients with diverse modalities into a global model without compromising privacy. Existing MFL methods suffer from two critical limitations: modality bias and task incompatibility. These two limitations stem from modality inconsistency and task heterogeneity among clients, which lead to degraded performance of the global server model on client-specific tasks. To tackle these problems, we introduce a multi-task compatible framework with a modality augmentation(MA) and a task-aware selective local feature aggregation (TA-SLFA). The designed MA and TA-SLFA modules respectively aim to tackle the modality bias and alleviate the task heterogeneity in MFL. Moreover, the task-aware dual-modal Low-Rank Adaptations (LoRAs) are integrated into a vision-language model, enhancing its ability to integrate task-specific features and improve multi-task learning ability. Extensive experiments and ablation analysis are conducted on four common public datasets and the experimental results demonstrate that our proposed model achieves significant improvements in multitask multimodal federated learning.",
            palabras_clave="multimodal federated learning, multi-task learning, vision-language models, low-rank adaptation, systems engineering, artificial intelligence",
            referencia_apa="Zeng, Y., Ren, H., Cai, Y., Li, Y., & Jing, Q. (2026). Modality augmentation and task-aware dual-modal LoRAs for multi-task multimodal federated learning. Information Processing & Management, 63, Article 104601. https://doi.org/10.1016/j.ipm.2025.104601",            
            busqueda_id=2
        )
        db.session.add(articulo4)   

        articulo5 = Articulo(
            titulo="Large language models for high-level computer-aided process planning in a distributed manufacturing paradigm. Robotics and Computer-Integrated.",
            autores="Stathatos, E., Benardos, P., Vosniakos, G.-C., Gross, D., & Spieker, H.",
            año=2026,
            revista="Robotics and Computer-Integrated Manufacturing, 100, Article 103233",
            resumen="This study applies Large Language Models (LLMs) to high-level Computer-Aided Process Planning (CAPP) in a distributed manufacturing context. It aims to generate alternative, feasible process chains for production of a wide range of parts. Parts are encoded in a custom encoding scheme supporting diverse part overall shapes, geometrical features within them, and corresponding manufacturing processes. The CAPP problem is formulated as a sequence prediction task, where a GPT-2-based LLM generates process chains autoregressively. To train and test the LLM a synthetic dataset of 7,840 unique parts and their alternative process chains was generated using expert-driven rule-based logic. The LLM is trained from scratch using a tokenization scheme treating part features and processes uniformly as discrete tokens, special tokens being employed to control sequence flow. Performance evaluation was performed for systematically reducing the size of the dataset. Finally, even with as little as 5% of the training data, the LLM achieves over 99% accuracy at the process chain-level. The extremely few spotted errors mainly involve minor secondary process mispredictions without critical failures. For comparison, a Recurrent Neural Network (RNN) was also trained with the same dataset. Since manufacturing data stemming from experts and not from sensors is notoriously difficult to collect, training a machine learning model with a dataset that is as small as possible is of utmost importance. In this light, the LLM proved superior to RNN, in fact emphatically so, the more the training dataset was limited.",
            palabras_clave="large language models, computer-aided process planning, distributed manufacturing, intelligent manufacturing systems, systems engineering, machine learning",
            referencia_apa="Stathatos, E., Benardos, P., Vosniakos, G.-C., Gross, D., & Spieker, H. (2026). Large language models for high-level computer-aided process planning in a distributed manufacturing paradigm. Robotics and Computer-Integrated Manufacturing, 83. https://doi.org/10.1016/j.rcim.2026.103233",            
            busqueda_id=2
        )
        db.session.add(articulo5)  

        articulo6 = Articulo(
            titulo="Optimizing distributed inference in healthcare IoT: Reinforcement learning and explainable AI for dynamic neural network pruning.",
            autores="Gaddam, V. G., Kalaivani, K., Ramakrishna, K. V. S. S., Singaraju, S., & Motupalli, R.",
            año=2026,
            revista="Expert Systems with Applications, 306, Article 131069",
            resumen="The rapid adoption of the Internet of Things (IoT) in healthcare has led to the proliferation of connected devices generating massive amounts of data, which require efficient processing and analysis. To address the challenge of performing distributed inference on these devices while managing limited computational resources, this paper proposes a novel framework that integrates reinforcement learning (RL) with dynamic pruning strategies, guided by explainable AI (XAI) techniques. The proposed RL-based dynamic pruning for distributed inference via XAI (RL-DPDX) ensures optimal resource utilization by selectively pruning model layers during inference without compromising model accuracy. Explainable AI is leveraged to enhance transparency and understanding of the pruning decisions, particularly in data-constrained environments. The paper presents a detailed system model, problem formulation, and a sub-optimal solution, followed by the development of the RL-DPDX framework, including environment design, state-action spaces, reward function, and agent architecture. Through extensive simulations, the framework’s performance is evaluated in a healthcare scenario, demonstrating significant improvements in computational efficiency, scalability, and adaptability compared to existing methods.",
            palabras_clave="reinforcement learning, distributed inference, healthcare iot, explainable ai, dynamic neural network pruning, systems engineering",
            referencia_apa="Gaddam, V. G., Kalaivani, K., Ramakrishna, K. V. S. S., Singaraju, S., & Motupalli, R. (2026). Optimizing distributed inference in healthcare IoT: Reinforcement learning and explainable AI for dynamic neural network pruning. Expert Systems with Applications, 239. https://doi.org/10.1016/j.eswa.2025.131069",            
            busqueda_id=2
        )
        db.session.add(articulo6)          

        articulo7 = Articulo(
            titulo="Intelligent parameter recommendation for substation design using knowledge graph and graph neural networks ",
            autores="Zhou, Liang., Gao, Zhen-Ting., Zhai, Pen-Fan., Zeng, Yi-Heng.",
            año=2026,
            revista="Energy Informatics",
            resumen="As power systems move toward digitalization and low-carbon transformation, improving the intelligence of substation design processes has become increasingly critical. Traditional equipment parameter selection relies heavily on manual experience and fragmented document retrieval, leading to inefficiencies, inconsistencies, and limited scalability. This paper proposes an intelligent parameter recommendation method tailored for substation engineering, integrating domain-specific knowledge graphs with adaptive graph neural networks (GNNs). The framework first extracts structured equipment information from multi-voltage substation design drawings using entity disambiguation, then constructs a hierarchical knowledge graph to represent inter-device relationships. A natural language interface captures user queries and encodes them into context-aware instruction vectors. These are used to guide a hybrid reasoning process that combines fuzzy rule matching and GNN-based relation inference. Case studies using real-world 10 kV/110 kV substation projects demonstrate that the proposed method significantly outperforms existing knowledge graph-based baselines in both accuracy and interpretability. The results show that this work is superior to the comparison baseline model in both ACC and AUC indicators, and support intelligent decision-making throughout the equipment lifecycle. This work provides a scalable solution for knowledge-driven substation design automation in the era of smart grids.",
            palabras_clave="artificial intelligence, power systems, substation design, knowledge graphs, graph neural networks, intelligent automation",
            referencia_apa="Zhou, Liang., Gao, Zhen-Ting., Zhai, Pen-Fan., Zeng, Yi-Heng. (2026). Intelligent parameter recommendation for substation design using knowledge graph and graph neural networks. Energy Informatics. https://doi.org/10.1186/s42162-025-00605-6",
            busqueda_id=3
        )
        db.session.add(articulo7)        

        articulo8 = Articulo(
            titulo="Emerging trends of recommender system for e-commerce: a comprehensive review.",
            autores="Rajpoot, C., Tiwari, V., Vishwakarma, S.",
            año=2026,
            revista="Discover Computing, 29, Article 63",
            resumen="With the rapid growth of online information, the recommender system (RSs) has become essential tools for filtering information and generating personalized recommendations for customers. These systems analyze individual user preferences, past reviews, and product ratings to enhance decision-making in the e-commerce sector. In this comprehensive review, several research articles published between 2020 and 2025 have been reviewed from various journals and conferences, covering multiple dimensions of recommender systems. The study emphasizes emerging techniques aimed at improving system performance. It begins by providing background information on recommender systems, including existing literature and prevailing research challenges. Furthermore, it explores cutting-edge methodologies such as machine learning, deep learning, large language models, and conversational recommender systems that are contributing to the evolution of RSs. Beyond traditional approaches, this review addresses significant research gaps and identifies key aspects influencing RS platforms. The ultimate goal of this study is to present a comprehensive understanding of the current state and future direction of recommender systems in the e-commerce industry.",
            palabras_clave="recommender systems, e-commerce, personalized recommendations, machine learning, deep learning, intelligent decision support systems",
            referencia_apa="Rajpoot, C., Tiwari, V., Vishwakarma, S. (2026) Emerging trends of recommender system for e-commerce: a comprehensive review. https://doi.org/10.1007/s10791-026-09923-z",
            busqueda_id=3
        )
        db.session.add(articulo8) 

        articulo9 = Articulo(
            titulo="From physics to machine learning and back: Part I - Learning with inductive biases in prognostics and health management (PHM).",
            autores="Fink, O., Sharma, V., Nejjar, I., Von Krannichfeldt, L., Garmaev, S., Zhang, Z., Wei, A.",
            año=2026,
            revista="Reliability Engineering & System Safety, 271, Article 112213",
            resumen="Prognostics and Health Management (PHM) is essential for ensuring the safe, reliable, and efficient operation of complex engineered systems by integrating fault detection, diagnostics, and prognostics into a unified framework. While machine learning (ML) has significantly advanced PHM by enabling data-driven decision-making, real-world challenges such as sparse or noisy data, limited labels, and complex degradation dynamics require approaches that go beyond purely data-driven modeling. This review focuses on inductive bias – the integration of prior knowledge, physical laws, and structural assumptions into ML model design – as a foundational mechanism to improve generalization, robustness, and interpretability in PHM. We explore the current state of the art in applying inductive bias to PHM, reviewing a wide range of methods including graph neural networks (relational biases), state-space models and neural ordinary differential equations (temporal biases), signal processing-inspired learning (spectral biases), neural operators (operator biases), causal representation learning (causal biases), and interpretable-by-design models (interpretability biases) through the use of inductive bias. For each method, we discuss its advantages, limitations, and suitability for different PHM tasks, and identify emerging applications where these techniques show strong potential. Furthermore, we examine how ML contributes back to physics understanding through symbolic regression (rediscovering physical laws) and post-hoc interpretation (transparent decision-making), closing the loop between physics understanding and modeling in PHM. By embedding domain knowledge into learning architectures, these approaches help constrain the hypothesis space and promote physically consistent learning, bridging the gap between theoretical modeling and real-world deployment in safety-critical applications. Part II of this review explores observational and learning biases, focusing on how data augmentation, representation, and training strategies shape model behavior and further enhance alignment between machine learning and the physical systems it aims to monitor and manage.",
            palabras_clave="prognostics and health management, inductive bias, physics-informed machine learning, system reliability engineering, interpretable machine learning, intelligent maintenance systems",
            referencia_apa="Fink, O., Sharma, V., Nejjar, I., Von Krannichfeldt, L., Garmaev, S., Zhang, Z., Wei, A., & Bizzi, A. (2026). From physics to machine learning and back: Part I – Learning with inductive biases in prognostics and health management (PHM). Reliability Engineering & System Safety, 271, Article 112213. https://doi.org/10.1016/j.ress.2026.112213",
            busqueda_id=3
        )
        db.session.add(articulo9)                     
        
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