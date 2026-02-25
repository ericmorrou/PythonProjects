import speech_recognition as sr
import json
import time

class VoiceService:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def capturar_voz(self):
        """
        Captura audio del micrófono y devuelve el texto reconocido y metadatos.
        Retorna: (texto, metadatos_dict)
        """
        try:
            with sr.Microphone() as source:
                print("Ajustando ruido ambiente...")
                self.recognizer.adjust_for_ambient_noise(source)
                print("Escuchando...")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                
                print("Procesando...")
                start_time = time.time()
                # recognize_google devuelve texto. Para confianza, necesitamos show_all=True
                response = self.recognizer.recognize_google(audio, show_all=True, language="es-ES")
                latency = round(time.time() - start_time, 2)

                if not response:
                    return None, {"status": "FAIL", "reason": "No speech detected", "latency": latency}
                
                # response format example: {'alternative': [{'transcript': 'hola', 'confidence': 0.98}, ...], 'final': True}
                
                if isinstance(response, dict) and 'alternative' in response:
                    best_match = response['alternative'][0]
                    texto = best_match.get('transcript')
                    confianza = best_match.get('confidence', 0.0)
                    
                    metadatos = {
                        "status": "OK",
                        "confianza": confianza,
                        "latencia": latency,
                        "alternativas": len(response['alternative'])
                    }
                    return texto, metadatos
                else:
                     return None, {"status": "FAIL", "reason": "Unknown format", "raw": str(response)}

        except sr.WaitTimeoutError:
            return None, {"status": "TIMEOUT", "reason": "No se detectó voz a tiempo"}
        except sr.RequestError as e:
            return None, {"status": "ERROR", "reason": f"API Error: {e}"}
        except sr.UnknownValueError:
            return None, {"status": "FAIL", "reason": "No se entendió el audio"}
        except Exception as e:
             return None, {"status": "ERROR", "reason": str(e)}
