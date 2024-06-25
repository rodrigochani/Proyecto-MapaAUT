from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit
import xml.etree.ElementTree as ET
import urllib.request

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Modificar plantilla (.qpt)'
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle(self.title)
        
        # Define los campos de texto como atributos de la clase
        self.label1 = QLabel("Número de expediente:")
        self.expdte = QLineEdit(self)
        self.label2 = QLabel("Padrón catastral:")
        self.padron = QLineEdit(self)
        self.label3 = QLabel("Responsable fiscal:")
        self.rfiscal = QLineEdit(self)
        self.label4 = QLabel("Municipio:")
        self.muni = QLineEdit(self)
        self.label5 = QLabel("Departamento:")
        self.dpto = QLineEdit(self)
        self.label6 = QLabel("Fuente de imagen:")
        self.fuente_img = QLineEdit(self)
        self.label7 = QLabel("Fecha de imagen:")
        self.fecha_img = QLineEdit(self)
        self.label8 = QLabel("Ruta del archivo para intersecar:")
        self.tointersect = QLineEdit()
        self.seleccionar = QPushButton("Seleccionar archivo")
        
        # Botón para ejecutar la función
        self.button_ejecutar = QPushButton('Ejecutar', self)
        self.button_ejecutar.clicked.connect(self.modificar_plantilla)
        
        # Etiqueta para mostrar el estado
        self.label = QLabel(self)
        
        # Diseño vertical (título y fuentes)
        layout = QVBoxLayout()
        layout.addWidget(self.label1)
        layout.addWidget(self.expdte)
        layout.addWidget(self.label2)
        layout.addWidget(self.padron)
        layout.addWidget(self.label3)
        layout.addWidget(self.rfiscal)
        layout.addWidget(self.label4)
        layout.addWidget(self.muni)
        layout.addWidget(self.label5)
        layout.addWidget(self.dpto)
        layout.addWidget(self.label6)
        layout.addWidget(self.fuente_img)
        layout.addWidget(self.label7)
        layout.addWidget(self.fecha_img)
        
        
        # Diseño vertical (cargar archivo y descargar padrón)
        layout.addWidget(self.label8)
        layout.addWidget(self.tointersect)
        layout.addWidget(self.seleccionar)
        layout.addWidget(self.button_ejecutar)
        layout.addWidget(self.label)
        
        
        # Establece el layout en la ventana
        self.setLayout(layout)
        self.show()
        
    def descargar_kml(self):
        numero_padron = self.padron.text()
        archivo_seleccionado = self.tointersect.text()
        nombre_carpeta = self.expdte.text()

        url = f"http://190.221.181.230:85/kml.asp?txtpadron={numero_padron}"

        # Carpeta de descarga
        if numero_padron or archivo_seleccionado:
            carpeta_descarga = os.path.join('C:/Users/Desktop/Desktop/Rodrigo/Proyecto MapaAUT', nombre_carpeta)
            # Si la no existe, crearla
        if not os.path.exists(carpeta_descarga):
            os.makedirs(carpeta_descarga)

                # Ruta completa del archivo a descargar
        ruta_descarga = f'C:/Users/Desktop/Desktop/Rodrigo/Proyecto MapaAUT/{nombre_carpeta}/padron_{numero_padron}'

        try:
            # Descargar el archivo
            urllib.request.urlretrieve(url, ruta_descarga)
            return ruta_descarga
        except urllib.error.HTTPError:
            return None

    def seleccionar_archivo(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo", "", "Shapefiles (*.shp);;All Files (*)")
        if filename:
            self.tointersect.setText(filename)
            
    
    def calcular_centroide(self, layer):
        # Asegurarse de que la capa tiene características
        if not layer.getFeatures():
            print("La capa no tiene características.")
            return None

        # Calcular el centroide de todas las características de la capa
        centroide = None
        for feature in layer.getFeatures():
            if centroide is None:
                centroide = feature.geometry().centroid()
        else:
            centroide = centroide.combine(feature.geometry().centroid())

        return centroide.asPoint()

    def ajustar_cuadro_a_centroide(self, capa_cuadro, centroide):
        
        cuadro_layer = QgsVectorLayer(capa_cuadro, "Cuadro", "ogr")
        
        if not cuadro_layer.isValid():
            print("La capa 'Cuadro' no se pudo cargar correctamente.")
            return

        # Crea una transformación desde EPSG:22173 (suponiendo que este es el SRC del centroide) a EPSG:4326
        transform = QgsCoordinateTransform(QgsCoordinateReferenceSystem("EPSG:22173"),
        QgsCoordinateReferenceSystem("EPSG:4326"),
        QgsProject.instance())

        # Intenta transformar el centroide
        try:
            centroide_transformado = transform.transform(centroide)
        except Exception as e:
            print(f"Error al transformar el centroide: {e}")
            return

        cuadro_layer.startEditing()

        for feature in cuadro_layer.getFeatures():
            geom = feature.geometry()
            cuadro_centroide = geom.centroid().asPoint()
            dx = centroide_transformado.x() - cuadro_centroide.x()
            dy = centroide_transformado.y() - cuadro_centroide.y()
            geom.translate(dx, dy)
            cuadro_layer.changeGeometry(feature.id(), geom)
            
        cuadro_layer.commitChanges()

    def modificar_plantilla(self):
        self.procesar_datos()
        self.modificar_nombre_titulo()
        self.modificar_nombre_fuentes()
        self.modificar_referencias()
        self.modificar_referencias_otbn()
        
        
    #Y:\Logos\logo flora y fauna 2020_.png
    
    def procesar_datos(self):
        ruta_kml = self.descargar_kml()

        # Si descargar_kml devuelve None, usar el archivo seleccionado
        archivo_interseccion =  ruta_kml if ruta_kml else self.tointersect.text()

        # Asumiendo que tienes otro archivo con el que realizar la intersección
        archivo_base = 'D:/OTBN - Rodrigo/Otros/Capas base/OTBN_Tucumán_postprocesado y unificado/OTBN_postprocesado_posgar98.shp'
        
        #Disolver archivo base, por si tiene dos objetos
        
        try:
            if archivo_interseccion:
                dissolved_init = processing.run("qgis:dissolve", {
                'INPUT': archivo_interseccion,
                'FIELD': [],
                'OUTPUT': 'memory:'
                })
        except:
            print ('Error: El archivo kml (descargado) no se puede abir o no tiene geometrías.') 
            self.close()
            
        # Intersección
        inter_result = processing.run("qgis:intersection", {
            'INPUT': archivo_base,
            'OVERLAY': dissolved_init['OUTPUT'],
            'OUTPUT': 'memory:'
        })

        # Disolución
        dissolved = processing.run("qgis:dissolve", {
            'INPUT': inter_result['OUTPUT'],
            'FIELD': ['color'],
            'OUTPUT': 'memory:'
            })
        
        # Obtener todos los nombres de campos de la capa dissolved
        all_fields = [field.name() for field in dissolved['OUTPUT'].fields()]

        if self.padron: 
            # Filtrar los campos que no queremos eliminar
            campos_a_mantener = ['Name', 'description', 'color', 'sup_ha']
        else:
            campos_a_mantener = ['color', 'sup_ha']

        campos_a_eliminar = [field for field in all_fields if field not in campos_a_mantener]
                
        nombre_carpeta = self.expdte.text()
                     
        # Obtener los índices de los campos a eliminar
        indexes_to_delete = [dissolved['OUTPUT'].fields().indexFromName(field) for field in campos_a_eliminar if dissolved['OUTPUT'].fields().indexFromName(field) != -1]
        
        if campos_a_eliminar:
            dissolved['OUTPUT'].startEditing()
            dissolved['OUTPUT'].deleteAttributes(indexes_to_delete)
            dissolved['OUTPUT'].commitChanges()
                    
        dissolved_cleaned = dissolved
        
        dissolved_with_area = processing.run("qgis:fieldcalculator", {
        'INPUT': dissolved_cleaned['OUTPUT'],
        'FIELD_NAME': 'sup_ha',
        'FIELD_TYPE': 0, # 0 indica que es un campo decimal (double)
        'FIELD_LENGTH': 10, 
        'FIELD_PRECISION': 2,
        'NEW_FIELD': False,  # Indica que no estamos creando un nuevo campo, sino actualizando uno existente
        'FORMULA': '$area / 10000',  # Fórmula para calcular la superficie y convertir de m² a hectáreas
        'OUTPUT': 'memory:'})
        
        dissolved_with_areaperc = processing.run("qgis:fieldcalculator", {
        'INPUT': dissolved_with_area['OUTPUT'],
        'FIELD_NAME': 'perc',
        'FIELD_TYPE': 0, # 0 indica que es un campo decimal (double)
        'FIELD_LENGTH': 10, 
        'FIELD_PRECISION': 2,
        'NEW_FIELD': True,  # Indica que estamos creando un nuevo campo, sino actualizando uno existente
        'FORMULA': '("sup_ha"*100)/(sum("sup_ha"))',  # Fórmula para porcentaje
        'OUTPUT': 'memory:'})
        
        # Eliminar filas por color
        colores_eliminar = ["NoData"]
        
        ids_eliminar = []
        
        fields = [field.name() for field in dissolved_with_areaperc['OUTPUT'].fields()]
        
        if "color" in fields:
            for feature in dissolved_with_areaperc['OUTPUT'].getFeatures():
                if feature["color"] in colores_eliminar:
                    ids_eliminar.append(feature.id())

        if ids_eliminar:
            dissolved_with_areaperc['OUTPUT'].startEditing()
            dissolved_with_areaperc['OUTPUT'].deleteFeatures(ids_eliminar)
            dissolved_with_areaperc['OUTPUT'].commitChanges()       

        numero_padron = self.padron.text()

        if dissolved_with_areaperc :
            # Guardar el archivo resultante en formato SHP
            output_file = f'C:/Users/Desktop/Desktop/Rodrigo/Proyecto MapaAUT/{nombre_carpeta}/padron_{numero_padron}_Int'
        else: 
            print ('No se logró una intersección. El padrón está vacío.')
        
        # Suponiendo que 'campo_para_contar' es el nombre del campo en el que estás interesado
        #campo_para_contar = 'color'

        # Obtener los índices de las características basadas en el campo específico
        indices = [feature["color"] for feature in dissolved_with_areaperc['OUTPUT'].getFeatures()]
                
        if len (indices) > 1 :
            dissolved_unique = processing.run("qgis:dissolve", {
            'INPUT': dissolved_with_areaperc['OUTPUT'],
            'FIELD': [],
            'OUTPUT': 'memory:'
            })
            
            dissolved_unique_with_area = processing.run("qgis:fieldcalculator", {
            'INPUT': dissolved_unique['OUTPUT'],
            'FIELD_NAME': 'sup_ha',
            'FIELD_TYPE': 0, # 0 indica que es un campo decimal (double)
            'FIELD_LENGTH': 10, 
            'FIELD_PRECISION': 3,
            'NEW_FIELD': False,  # Indica que no estamos creando un nuevo campo, sino actualizando uno existente
            'FORMULA': '$area / 10000',  # Fórmula para calcular la superficie y convertir de m² a hectáreas
            'OUTPUT': 'memory:'
            })
            dissolved_unique_with_areaperc = processing.run("qgis:fieldcalculator", {
            'INPUT': dissolved_unique_with_area['OUTPUT'],
            'FIELD_NAME': 'perc',
            'FIELD_TYPE': 0, # 0 indica que es un campo decimal (double)
            'FIELD_LENGTH': 10, 
            'FIELD_PRECISION': 2,
            'NEW_FIELD': False,  # Indica que estamos creando un nuevo campo, sino actualizando uno existente
            'FORMULA': '("sup_ha"*100)/(sum("sup_ha"))',  # Fórmula para porcentaje
            'OUTPUT': 'memory:'})
        else:
            dissolved_unique = dissolved_with_areaperc
        
        
        
        if dissolved_unique_with_areaperc :
            # Guardar el archivo resultante en formato shp
            output_file = f'C:/Users/Desktop/Desktop/Rodrigo/Proyecto MapaAUT/{nombre_carpeta}/padron_{numero_padron}_Int_Dis'
            output_file2 = f'C:/Users/Desktop/Desktop/Rodrigo/Proyecto MapaAUT/{nombre_carpeta}/padron_{numero_padron}_Int'
            output_file3 = f'C:/Users/Desktop/Desktop/Rodrigo/Proyecto MapaAUT/{nombre_carpeta}/padron_{numero_padron}'
            # Guardamos el resultado como SHP
            QgsVectorFileWriter.writeAsVectorFormat(dissolved_unique_with_areaperc['OUTPUT'], output_file, "utf-8", dissolved_unique_with_areaperc['OUTPUT'].crs(), "ESRI Shapefile")
            print(f"Resultado guardado en {output_file}")
            QgsVectorFileWriter.writeAsVectorFormat(dissolved_with_areaperc['OUTPUT'], output_file2, "utf-8", dissolved_with_areaperc['OUTPUT'].crs(), "ESRI Shapefile")
            print(f"Resultado guardado en {output_file2}")
            
        else: 
            print ('No se guardaron los archivos SHP')
        
        # Agregar la capas SHP a QGIS
        shp_layer = QgsVectorLayer(output_file + ".shp", f"{numero_padron}_Int_Dis", "ogr")
        if shp_layer.isValid():
            QgsProject.instance().addMapLayer(shp_layer)
       
        shp_layer2 = QgsVectorLayer(output_file2 + ".shp", f"{numero_padron}_Int", "ogr")
        if shp_layer2.isValid():
            QgsProject.instance().addMapLayer(shp_layer2)

        # Agregar la capa KML a QGIS
        kml_layer = QgsVectorLayer(output_file3, f"{numero_padron}_padron", "ogr")
        if kml_layer.isValid():
            QgsProject.instance().addMapLayer(kml_layer)
        
              
        
        # Uso de la función
        centroide = self.calcular_centroide(dissolved_unique_with_areaperc['OUTPUT'])
        
        print(f"Coordenadas del centroide antes de la transformación: X={centroide.x()}, Y={centroide.y()}")
        
        if centroide is None or math.isinf(centroide.x()) or math.isinf(centroide.y()):
            print("Centroide inválido o indefinido.")
            return

        if centroide:
            self.ajustar_cuadro_a_centroide("C:/Users/Desktop/Desktop/Rodrigo/Certificados de obra/Mapas CO - 2017/Otros/Cuadro.shp", centroide)

    

    def modificar_nombre_titulo(self):
        ruta_qpt = r'C:\Users\Desktop\Desktop\Rodrigo\Proyecto MapaAUT\Plantilla.qpt'
        texto_id = "Mapa catastral"
                
        
        # Obtener el nuevo texto del campo de entrada
        nuevo_texto =  f'<b>MAPA CATASTRAL CATEGORIZADO SEGÚN LEY PROVINCIAL N° 8304: EXPDTE. N° {self.expdte.text()} </b><br> <b>Padrón catastral:</b><i> {self.padron.text()} </i><br> <b>Responsable fiscal:</b><i> {self.rfiscal.text()} </i><br> <b>Municipio: </b><i> {self.muni.text()} </i><br> <b>Departamento: </b><i> {self.dpto.text()} </i>' 
        
        # Si el campo está vacío, no hacer nada
        if not nuevo_texto.strip():
            self.label.setText("Por favor, introduce todos los campos.")
            return
        
        # Parsear el archivo .qpt
        tree = ET.parse(ruta_qpt)
        root = tree.getroot()

        # Buscar todos los elementos LayoutItem y modificar el atributo 'id' que coincida con "Mapa catastral"
        for elem in root.findall(".//LayoutItem"):
            id_elem = elem.attrib.get('id')
            if id_elem == texto_id:
                elem.set('labelText', nuevo_texto)
                break

        # Guardar las modificaciones al archivo .qpt
        tree.write(ruta_qpt, encoding='utf-8', xml_declaration=True)
        
                
    def modificar_nombre_fuentes(self):
        ruta_qpt = r'C:\Users\Desktop\Desktop\Rodrigo\Proyecto MapaAUT\Plantilla.qpt'
        texto_id = "Fuentes"       
                
        # Obtener el nuevo texto del campo de entrada
        nuevo_texto =  f'<b>FUENTES:</b><br> <i>Dirección General de Catastro - DGC<br> Instituto Geográfico Nacional - IGN<br> Fundación ProYungas<br> RIDES<br> Imágenes {self.fuente_img.text()}:<br>  ({self.fecha_img.text()})<br>' 
        
        # Si el campo está vacío, no hacer nada
        if not nuevo_texto.strip():
            self.label.setText("Por favor, introduce todos los campos.")
            return
        
        # Parsear el archivo .qpt
        tree = ET.parse(ruta_qpt)
        root = tree.getroot()

        # Buscar todos los elementos LayoutItem y modificar el atributo 'id' que coincida con "Mapa catastral"
        for elem in root.findall(".//LayoutItem"):
            id_elem = elem.attrib.get('id')
            if id_elem == texto_id:
                elem.set('labelText', nuevo_texto)
                break

        # Guardar las modificaciones al archivo .qpt
        tree.write(ruta_qpt, encoding='utf-8', xml_declaration=True)
        
       
    
    def modificar_referencias(self):
        ruta_qpt = r'C:\Users\Desktop\Desktop\Rodrigo\Proyecto MapaAUT\Plantilla.qpt'
        texto_title = "REFERENCIAS:"
        texto_id = "parcelario_utm_nuevo_355c5ac3_6eb6_446e_a9c1_e67f88cf6b66"       

        nombre_carpeta = self.expdte.text()
        numero_padron = self.padron.text()
    
        # Suponiendo que dissolved_unique_with_areaperc es una referencia válida a tu capa
        layer_path = f'C:/Users/Desktop/Desktop/Rodrigo/Proyecto MapaAUT/{nombre_carpeta}/padron_{numero_padron}_Int_Dis.shp'
        layer = QgsVectorLayer(layer_path, "layer", "ogr")
        
        # Verificar si la capa es válida
        if not QgsVectorLayer.isValid(layer):
            print("La capa no es válida")
        else:
            print("La capa es válida")
        # Iterar sobre las características de la capa
        for feature in layer.getFeatures():
            # Obtener el valor del atributo 'sup_ha'
            valor_sup_ha = feature['sup_ha']
            print(f"Valor de 'sup_ha': {valor_sup_ha}")
    
        # Obtener el nuevo texto del campo de entrada
        nuevo_texto =  f'Padrón N°: {numero_padron} ({valor_sup_ha:.2f} ha)'
        
        # Si el campo está vacío, no hacer nada
        if not nuevo_texto.strip():
            self.label.setText("Por favor, introduce todos los campos.")
            return
    
        # Parsear el archivo .qpt
        tree = ET.parse(ruta_qpt)
        root = tree.getroot()

        # Buscar todos los elementos LayoutItem y modificar el atributo 'id' que coincida con "Mapa catastral"
        for layout_item in root.findall(".//LayoutItem"):
            if layout_item.get('title') == texto_title:
                layer_tree_layer = layout_item.find(f".//layer-tree-layer[@id='{texto_id}']")
                if layer_tree_layer is not None:
                    custom_properties = layer_tree_layer.find('customproperties')
                    if custom_properties is not None:
                        for option in custom_properties.findall('Option'):
                            if option.get ('type') == 'Map':
                                for sub_option in option.findall('Option'):
                                    if sub_option.get('name') == 'legend/label-1':
                                        sub_option.set('value', nuevo_texto)
                                        break

        # Guardar las modificaciones al archivo .qpt
        tree.write(ruta_qpt, encoding='utf-8', xml_declaration=True)
        
    def modificar_referencias_otbn(self):
        ruta_qpt = r'C:\Users\Desktop\Desktop\Rodrigo\Proyecto MapaAUT\Plantilla.qpt'
        texto_title = "REFERENCIAS:"
        texto_id = "OTBN_UTM20190201112644660"       

        nombre_carpeta = self.expdte.text()
        numero_padron = self.padron.text()
    
        # Suponiendo que dissolved_unique_with_areaperc es una referencia válida a tu capa
        layer_path = f'C:/Users/Desktop/Desktop/Rodrigo/Proyecto MapaAUT/{nombre_carpeta}/padron_{numero_padron}.kml'
        layer = QgsVectorLayer(layer_path, "layer", "ogr")
        layer_path2= f'C:/Users/Desktop/Desktop/Rodrigo/Proyecto MapaAUT/{nombre_carpeta}/padron_{numero_padron}_Int.shp'
        layer2 = QgsVectorLayer(layer_path2, "layer2", "ogr")
                        
        # Verificar si la capa es válida
        if not QgsVectorLayer.isValid(layer):
            print("La capa no es válida")
        else:
            print("La capa es válida")
            
        if layer:
                layer_diss = processing.run("qgis:dissolve", {
                'INPUT': layer,
                'FIELD': [],
                'OUTPUT': 'memory:'
                }) 
                
                layer_diss_area = processing.run("qgis:fieldcalculator", {
                'INPUT': layer_diss['OUTPUT'],
                'FIELD_NAME': 'sup_ha',
                'FIELD_TYPE': 0, # 0 indica que es un campo decimal (double)
                'FIELD_LENGTH': 10, 
                'FIELD_PRECISION': 2,
                'NEW_FIELD': True,  # Indica que estamos creando un nuevo campo, sino actualizando uno existente
                'FORMULA': '$area / 10000',  # Fórmula para calcular la superficie y convertir de m² a hectáreas
                'OUTPUT': 'memory:'
                })
                
        
        sum = 0
        
        # Iterar sobre las características de la capa
        for feature in layer_diss_area.getFeatures():
            # Obtener el valor del atributo 'sup_ha'
            valor_sup_ha = feature['sup_ha']
            sum = valor_sup_ha + sum
            print(f"Valor total de 'sup_ha': {sum}")
        
        if not layer2.isValid():
            print("La segunda capa no es válida")
        else:
            print("La segunda capa es válida")
        
        for feature in layer2.getFeatures():
            if feature['color'] == 'Rojo':
                # Obtener el valor del atributo 'sup_ha'
                valor_sup_ha_c1 = feature['sup_ha']
                valor_perc_c1 = feature['perc']                
                print(f"Valor de 'Cat I': {valor_sup_ha_c1}")
            elif feature['color'] == 'Amarillo':
                # Obtener el valor del atributo 'sup_ha'
                valor_sup_ha_c2 = feature['sup_ha']
                valor_perc_c2 = feature['perc']                
                print(f"Valor de 'Cat II': {valor_sup_ha_c2}")
            elif feature['color'] == 'Verde':
                # Obtener el valor del atributo 'sup_ha'
                valor_sup_ha_c3 = feature['sup_ha']
                valor_perc_c3 = feature['perc']                
                print(f"Valor de 'Cat III': {valor_sup_ha_c3}")
            elif feature['color'] == 'Marron Oscuro':
                # Obtener el valor del atributo 'sup_ha'
                valor_sup_ha_a = feature['sup_ha']
                valor_perc_a = feature['perc']                
                print(f"Valor de 'Cat A': {valor_sup_ha_a}")
            elif feature['color'] == 'Marron Claro':
                # Obtener el valor del atributo 'sup_ha'
                valor_sup_ha_b = feature['sup_ha']
                valor_perc_b = feature['perc']                
                print(f"Valor de 'Cat B': {valor_sup_ha_b}")
    
        # Obtener el nuevo texto del campo de entrada
        nuevo_texto1 =  f'OTBN (Ley Prov. N° 8304) - {valor_sup_ha:.2f} ha:'
        nuevo_texto2 =  f'Categoría II - {valor_sup_ha_c2:.2f} ha ({valor_perc_c2:.2f} %)'
        nuevo_texto3 =  f'Categoría B - {valor_sup_ha_b:.2f} ha ({valor_perc_b:.2f} %)'
        nuevo_texto4 =  f'Categoría A - {valor_sup_ha_a:.2f} ha ({valor_perc_a:.2f} %)'
        nuevo_texto5 =  f'Categoría I - {valor_sup_ha_c1:.2f} ha ({valor_perc_c1:.2f} %)'
        nuevo_texto6 =  f'Categoría III - {valor_sup_ha_c3:.2f} ha ({valor_perc_c3:.2f} %)'
        
           
        # Parsear el archivo .qpt
        tree = ET.parse(ruta_qpt)
        root = tree.getroot()

        # Buscar todos los elementos LayoutItem y modificar el atributo 'id' que coincida con "Mapa catastral"
        for layout_item in root.findall(".//LayoutItem"):
            if layout_item.get('title') == texto_title:
                layer_tree_layer = layout_item.find(f".//layer-tree-layer[@id='{texto_id}']")
                if layer_tree_layer is not None:
                    custom_properties = layer_tree_layer.find('customproperties')
                    if custom_properties is not None:
                        for option in custom_properties.findall('Option'):
                            if option.get ('type') == 'Map':
                                for sub_option in option.findall('Option'):
                                    if sub_option.get('name') == 'legend/title-label' or sub_option.get('name') == 'cached_name':
                                        sub_option.set('value', nuevo_texto1)
                                    if sub_option.get('name') == 'legend/label-0':
                                        sub_option.set('value', nuevo_texto2)
                                    if sub_option.get('name') == 'legend/label-1':
                                        sub_option.set('value', nuevo_texto3)
                                    if sub_option.get('name') == 'legend/label-2':
                                        sub_option.set('value', nuevo_texto4)
                                    if sub_option.get('name') == 'legend/label-3':
                                        sub_option.set('value', nuevo_texto5)
                                    if sub_option.get('name') == 'legend/label-4':
                                        sub_option.set('value', nuevo_texto6)    
                                        

        # Guardar las modificaciones al archivo .qpt
        tree.write(ruta_qpt, encoding='utf-8', xml_declaration=True)
        
        # Actualizar el estado en la etiqueta
        self.label.setText("Plantilla modificada exitosamente.")
        
        #Cerrar ventana
        self.close()
        
# Creamos y mostramos la ventana
window = App()