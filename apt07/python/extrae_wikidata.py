#-*- coding: UTF-8 -*-
import sys, os
import json
import urllib2

class datos_parlamentarios:
    
    def lee_wikidata(self,url):
        return urllib2.urlopen(url).read()
    
    def convierte_json(self,datos):
        return json.loads(datos)
    
    def lee_wikidata_json(self,url):
        datos=self.lee_wikidata(url)
        if len(datos)>0:
            jsonData=self.convierte_json(datos)
            if len(jsonData)>0:
                return jsonData
            else:
                return {}
        else:
            return {}

    def obtiene_valores_propiedad_entidad(self,entidad,propiedad):
        arrvalores=[]
        url='https://www.wikidata.org/w/api.php?action=wbgetclaims&format=json&entity=%s&property=%s' % (entidad,propiedad)
        jsonData=self.lee_wikidata_json(url)
        valores=jsonData['claims'][propiedad]
        for valor in valores:
            dictValor=dict()
            value=valor['mainsnak']['datavalue']['value']
            if 'id' in value:
                entidad=value['id']
                url='https://www.wikidata.org/w/api.php?action=wbgetentities&ids=%s&format=json&props=labels&languages=es' % entidad
                jsonDataId=self.lee_wikidata_json(url)
                cargo=jsonDataId['entities'][entidad]['labels']['es']['value']
                dictValor['cargo']=cargo
            valPropiedades=valor['qualifiers']
            for prop in valPropiedades:
                valProp=valPropiedades[prop][0]['datavalue']['value']
                if prop=='P580' or prop=='P582':
                    if 'time' in valProp:
                        if prop=='P580':
                            inicio=valProp['time']
                            dictValor['inicio']=inicio
                        elif prop=='P582':
                            fin=valProp['time']
                            dictValor['fin']=fin
                if prop=='P4100' or prop=='P2937':
                    if 'id' in valProp:
                        entidad=valProp['id']
                        url='https://www.wikidata.org/w/api.php?action=wbgetentities&ids=%s&format=json&props=labels&languages=es' % entidad
                        jsonDataId=self.lee_wikidata_json(url)
                        if prop=='P4100':
                            partido=jsonDataId['entities'][entidad]['labels']['es']['value']
                            dictValor['partido']=partido
                        elif prop=='P2937':
                            periodolegislativo=jsonDataId['entities'][entidad]['labels']['es']['value']
                            dictValor['periodolegislativo']=periodolegislativo
                            
            arrvalores.append(dictValor)
            
        return arrvalores
        #if isinstance(valor, str) or isinstance(valor, unicode):
            #return valor
        #else:
            #if 'id' in valor:
                #entidad=valor['id']
                #url='https://www.wikidata.org/w/api.php?action=wbgetentities&ids=%s&format=json&props=labels&languages=es' % entidad
                #jsonData=self.lee_wikidata_json(url)
                #return jsonData['entities'][entidad]['labels']['es']['value']
            #elif 'time' in valor:
                #return valor['time']
            #else:
                #return ''
            
    def obtiene_propiedad_entidad(self,entidad,propiedad):
        url='https://www.wikidata.org/w/api.php?action=wbgetclaims&format=json&entity=%s&property=%s' % (entidad,propiedad)
        jsonData=self.lee_wikidata_json(url)
        valor=jsonData['claims'][propiedad][0]['mainsnak']['datavalue']['value']
        if isinstance(valor, str) or isinstance(valor, unicode):
            return valor
        else:
            if 'id' in valor:
                entidad=valor['id']
                url='https://www.wikidata.org/w/api.php?action=wbgetentities&ids=%s&format=json&props=labels&languages=es' % entidad
                jsonData=self.lee_wikidata_json(url)
                return jsonData['entities'][entidad]['labels']['es']['value']
            elif 'time' in valor:
                return valor['time']
            else:
                return ''
    
    def obtiene_url_imagen(self,imagen):
        imagen=imagen.replace(' ','_')
        url='https://commons.wikimedia.org/w/api.php?action=query&format=json&formatversion=2&prop=imageinfo&iiprop=url&iiurlwidth=320&titles=File:%s' % imagen
        jsonData=self.lee_wikidata_json(url)
        return jsonData['query']['pages'][0]['imageinfo'][0]['thumburl'],jsonData['query']['pages'][0]['imageinfo'][0]['url']
    
    def genera_archivo_json(self, archivo, datos):
        with open(archivo, 'w') as f:
            json.dump(datos, f)
        f.close()
        
    def procesa_datos_parlamentarios(self,url,archivoPersonas):
        arrPersona=[]
        jsonData=self.lee_wikidata_json(url)
        if len(jsonData)>0:
            if jsonData['success']==1:
                for jsonEntidad in jsonData['entities']:
                    entidad=jsonData['entities'][jsonEntidad]['id']
                    label=jsonData['entities'][jsonEntidad]['labels']['es']['value']
                    description=jsonData['entities'][jsonEntidad]['descriptions']['es']['value']
                    persona=dict()
                    persona['entidad']=entidad
                    persona['label']=label
                    persona['description']=description
                    persona['url']='https://www.wikidata.org/wiki/%s' % entidad
                    
                    propiedad='P18'
                    imagen=self.obtiene_propiedad_entidad(entidad, propiedad)
                    thumburl,imgurl=self.obtiene_url_imagen(imagen)
                    
                    persona['thumburl']=thumburl
                    persona['imgurl']=imgurl
                    
                    propiedad='P21'
                    genero=self.obtiene_propiedad_entidad(entidad, propiedad)                    
                    persona['genero']=genero

                    propiedad='P19'
                    lugarnacimiento=self.obtiene_propiedad_entidad(entidad, propiedad)                    
                    persona['lugarnacimiento']=lugarnacimiento

                    propiedad='P569'
                    fechanacimiento=self.obtiene_propiedad_entidad(entidad, propiedad)                    
                    persona['fechanacimiento']=fechanacimiento
                    
                    propiedad='P102'
                    partidopolitico=self.obtiene_propiedad_entidad(entidad, propiedad)                    
                    persona['partidopolitico']=partidopolitico
                    
                    propiedad='P39'
                    cargos=self.obtiene_valores_propiedad_entidad(entidad, propiedad)
                    persona['cargos']=cargos
                    
                    self.genera_archivo_json(entidad+'.json',persona)
                    
                    arrPersona.append(persona)
        if len(arrPersona)>0:
            self.genera_archivo_json(archivoPersonas,arrPersona)

d=datos_parlamentarios()
url='https://www.wikidata.org/w/api.php?action=wbgetentities&ids=Q451359|Q5832999|Q8846905&format=json&props=labels|descriptions&languages=es'
archivoPersonas='personas.json'
d.procesa_datos_parlamentarios(url,archivoPersonas)
