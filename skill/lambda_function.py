import logging

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, AbstractExceptionHandler,
    AbstractResponseInterceptor, AbstractRequestInterceptor)
from ask_sdk_core.utils import is_intent_name, is_request_type
from ask_sdk_core.utils.request_util import get_slot_value

from ask_sdk_model.dialog import (
    ElicitSlotDirective, DelegateDirective)
from ask_sdk_model import (
    Response, IntentRequest, DialogState, SlotConfirmationStatus, Slot)
from ask_sdk_model.slu.entityresolution import StatusCode
from ask_sdk_model.ui import SimpleCard

import trails

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class AbstractRequestHandlerLog(AbstractRequestHandler):
    def log_request(self, handler_input):
        logger.info("REQUEST: {}".format(handler_input.request_envelope.to_str()))
    
    def log_response(self, handler_input):
        logger.info("RESPONSE: {}".format(handler_input.response_builder.response.to_str()))

class OpenIntentHandler(AbstractRequestHandlerLog):
    def can_handle(self, handler_input):
        return is_intent_name("OpenIntent")(handler_input)

    def handle(self, handler_input):
        self.log_request(handler_input)
        t = trails.Trails()
        speech_text = t.summary("open")
        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Open Trails", speech_text)).set_should_end_session(True)
        self.log_response(handler_input)
        return handler_input.response_builder.response

class ClosedIntentHandler(AbstractRequestHandlerLog):
    def can_handle(self, handler_input):
        return is_intent_name("ClosedIntent")(handler_input)

    def handle(self, handler_input):
        self.log_request(handler_input)
        t = trails.Trails()
        speech_text = t.summary("closed")
        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Closed Trails", speech_text)).set_should_end_session(True)
        self.log_response(handler_input)
        return handler_input.response_builder.response

class SummaryIntentHandler(AbstractRequestHandlerLog):
    def can_handle(self, handler_input):
        return is_intent_name("SummaryIntent")(handler_input)

    def handle(self, handler_input):
        self.log_request(handler_input)
        t = trails.Trails()
        speech_text = t.summary()
        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Trail Status", speech_text)).set_should_end_session(True)
        self.log_response(handler_input)
        return handler_input.response_builder.response

class TrailIntentHandler(AbstractRequestHandlerLog):
    def can_handle(self, handler_input):
        return is_intent_name("TrailIntent")(handler_input)

    def handle(self, handler_input):
        self.log_request(handler_input)
        t = trails.Trails()
        #speech_text = t.summary("closed")
        slot_trail = get_slot_value(handler_input, "trail")
        matched_trails = t.get_trail(slot_trail)
        speech_text = ""
        for trail in matched_trails:
            speech_text += "{} is {}. Updated {} ago. ".format(trail.name(), trail.status(), trail.age())
        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Trail", speech_text)).set_should_end_session(True)
        self.log_response(handler_input)
        return handler_input.response_builder.response
    
class HelpIntentHandler(AbstractRequestHandlerLog):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        self.log_request(handler_input)
        speech_text = """
            I can provide status for all the trails listed on triangle MTB dot com.  You can ask me questions like:
                What trails are open?
                Can I ride Beaver Dam?
                Is San Lee open?
                Summary of all trails?
        """
        handler_input.response_builder.speak(speech_text).ask(speech_text).set_card(
            SimpleCard("Help", speech_text))
        self.log_response(handler_input)
        return handler_input.response_builder.response

class LaunchRequestHandler(HelpIntentHandler):
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)

class AllExceptionHandler(AbstractExceptionHandler):

    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        # Log the exception in CloudWatch Logs
        logger.error(exception)

        speech = "Sorry, I didn't get it. Can you please say it again!!"
        handler_input.response_builder.speak(speech).ask(speech)
        return handler_input.response_builder.response

sb = SkillBuilder()
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(OpenIntentHandler())
sb.add_request_handler(ClosedIntentHandler())
sb.add_request_handler(TrailIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(SummaryIntentHandler())

sb.add_exception_handler(AllExceptionHandler())

handler = sb.lambda_handler()
