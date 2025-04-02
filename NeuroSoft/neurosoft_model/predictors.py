import numpy as np
import nibabel as nib
import tensorflow as tf
import os
from django.conf import settings
from PIL import Image
import io
import logging

logger = logging.getLogger(__name__)

class DerramePredictor:
    def __init__(self):
        try:
            model_path = os.path.join(settings.BASE_DIR, 'neurosoft_model', 'models', 'modelo_deteccion_derrames1.h5')
            self.model = tf.keras.models.load_model(model_path)
            logger.info("Modelo de IA cargado correctamente")
        except Exception as e:
            logger.error(f"Error al cargar el modelo: {str(e)}")
            raise

    def load_nifti_image(self, file_path):
        """Carga y preprocesa imágenes NIfTI"""
        try:
            img = nib.load(file_path).get_fdata()
            img = np.interp(img, (img.min(), img.max()), (0, 1))  # Normalizar
            img = np.resize(img, (128, 128, 128))  # Redimensionar
            img = img[..., np.newaxis]  # Agregar dimensión de canal
            return img
        except Exception as e:
            logger.error(f"Error al cargar imagen NIfTI: {str(e)}")
            raise

    def extract_sample_slice(self, volume):
        """Extrae una slice representativa del volumen 3D"""
        try:
            middle_slice = volume.shape[2] // 2
            slice_2d = volume[:, :, middle_slice, 0]
            return (slice_2d * 255).astype(np.uint8)  # Convertir a 8-bit para imagen
        except Exception as e:
            logger.error(f"Error al extraer slice: {str(e)}")
            raise

    def predict(self, file_path):
        """Realiza la predicción sobre un archivo"""
        try:
            # Verificar si el archivo existe
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Archivo no encontrado: {file_path}")

            # Cargar y preprocesar imagen
            img_volume = self.load_nifti_image(file_path)
            img = np.expand_dims(img_volume, axis=0)  # Agregar dimensión de batch
            
            # Realizar predicción
            prediction = self.model.predict(img)[0]
            max_index = np.argmax(prediction)
            
            # Mapear resultados
            prediction_map = {
                0: 'Poco probable',
                1: 'Probable',
                2: 'Muy probable'
            }
            
            # Obtener slice representativa
            sample_slice = self.extract_sample_slice(img_volume)
            pil_image = Image.fromarray(sample_slice)
            
            # Convertir imagen a bytes
            img_byte_arr = io.BytesIO()
            pil_image.save(img_byte_arr, format='PNG')
            img_bytes = img_byte_arr.getvalue()
            
            return {
                'prediccion': prediction_map[max_index],
                'precision': float(prediction[max_index]) * 100,
                'imagen_bytes': img_bytes,
                'probabilidades': prediction.tolist(),
                'resumen': f"Predicción: {prediction_map[max_index]} ({prediction[max_index]*100:.2f}%)\n" +
                          f"Distribución: Poco probable: {prediction[0]*100:.2f}%, " +
                          f"Probable: {prediction[1]*100:.2f}%, " +
                          f"Muy probable: {prediction[2]*100:.2f}%",
                'estado': 'Finalizado'
            }
            
        except Exception as e:
            logger.error(f"Error en predicción: {str(e)}")
            return {
                'prediccion': 'Error',
                'precision': 0.0,
                'imagen_bytes': None,
                'probabilidades': [0.0, 0.0, 0.0],
                'resumen': f"Error en procesamiento: {str(e)}",
                'estado': 'Error'
            }