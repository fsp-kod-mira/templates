import grpc
import templates_pb2
import templates_pb2_grpc
from grpc_reflection.v1alpha import reflection
from concurrent import futures
import logging
import model
import os


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

grpc_port = os.environ.get('GRPC_IPPORT') or '0.0.0.0:50051'



class TemplatesServicer(templates_pb2_grpc.TemplatesServicer):
    
    def CreateTemplate(self, request, context):
        """
        Добавление шаблона
        """
        logger.info("CreateTemplate request")
        try:
            id = model.AddTemplate(request.name, request.description)
            return templates_pb2.IdStruct(id=id)
        except Exception as e:
            logger.error(f"Error in CreateTemplate: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return templates_pb2.IdStruct()


    def CreateLink(self, request, context):
        """
        Создание связи между таблицами
        """
        logger.info("CreateLink request")
        try:
            id = model.AddFeatureTemplateLink(request.feature_id, request.template_id)
            return templates_pb2.IdStruct(id=id)
        except Exception as e:
            logger.error("Error in CreateLink:", e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return templates_pb2.IdStruct()


    def GetAllTemplates(self, request, context):
        """
        Получение всех шаблонов
        """
        logger.info("GetAllTemplates request")
        try:
            ret_templates = templates_pb2.TemplatesList()
            templates_result = model.GetAllTemplates()

            for template in templates_result:
                temp_struct = templates_pb2.TemplateStruct(id=template["id"],
                    name=template["name"], 
                    description=template["description"])
                ret_templates.items.append(temp_struct)

            return ret_templates
        except Exception as e:
            logger.error("Error in GetAllTemplates:", e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return templates_pb2.TemplatesList()


    def GetFeaturesByTemplateId(self, request, context):
        """
        Получение фич по айди шаблона
        """
        logger.info("GetFeaturesByTemplateId request")
        try:
            ret_features = templates_pb2.FeaturesList()
            templates_result = model.GetFeaturesByTemplateId(request.id)
            
            for feature in templates_result:
            
                temp_struct = templates_pb2.FeatureStruct(id=feature["id"], name=feature["name"])
                
                ret_features.items.append(temp_struct)

            return ret_features
        except Exception as e:
            logger.error("Error in GetFeaturesByTemplateId:", e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return templates_pb2.FeaturesList()
        

    def DeleteLink(self, request, context):
        """
        Удалить связь между таблицами
        """
        logger.info("DeleteLink request")
        try:
            
            model.DeleteFeatureTemplateLink(request.feature_id, request.template_id)
        except Exception as e:
            logger.error("Error in DeleteLink:", e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
        
        return templates_pb2.Empty()


    def DeleteTemplate(self, request, context):
        """
        Удалить шаблон
        """
        logger.info("DeleteTemplate request")
        try:
            model.DeleteTemplate(request.id)
        except Exception as e:
            logger.error("Error in DeleteTemplate:", e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
        
        return templates_pb2.Empty()


    def CreateFeature(self, request, context):
        """
        Создание фичи
        """
        logger.info("CreateFeature request")

        try:
            id = model.AddFeature(request.name)
            return templates_pb2.IdStruct(id=id)
        except Exception as e:
            logger.error("Error in DeleteTemplate:", e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return templates_pb2.Empty()    








def serve():
    try:
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        templates_pb2_grpc.add_TemplatesServicer_to_server(TemplatesServicer(), server)
        SERVICE_NAMES = (
            templates_pb2.DESCRIPTOR.services_by_name['Templates'].full_name,
            reflection.SERVICE_NAME,
        )

        reflection.enable_server_reflection(SERVICE_NAMES, server)
        server.add_insecure_port(grpc_port)
        server.start()
        server.wait_for_termination()
    except Exception as e:
        logger.error("Error in server:", e)


if __name__ == "__main__":
    logger.info(f"Run server on {grpc_port}")
    serve()
