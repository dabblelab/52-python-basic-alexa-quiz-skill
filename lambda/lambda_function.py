"""
 Copyright (C) 2020 Dabble Lab - All Rights Reserved
 You may use, distribute and modify this code under the
 terms and conditions defined in file 'LICENSE.txt', which
 is part of this source code package.
 
 For additional copyright information please
 visit : http://dabblelab.com/copyright
 """

from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.dispatch_components import (AbstractRequestHandler, AbstractExceptionHandler, AbstractRequestInterceptor, AbstractResponseInterceptor)
from ask_sdk_core.skill_builder import SkillBuilder

import logging
import json
import random
import os

quiz_data = json.loads(open('quiz_data.json').read())
options_key = ["A","B","C","D"]

# Initializing the logger and setting the level to "INFO"
# Read more about it here https://www.loggly.com/ultimate-guide/python-logging-basics/
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Intent Handlers

#This Handler is called when the skill is invoked by using only the invocation name(Ex. Alexa, open template four)
class LaunchRequestHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)
    
    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        session_attributes = handler_input.attributes_manager.session_attributes
        
        speech_output = random.choice(language_prompts["GREETING"])
        reprompt = random.choice(language_prompts["GREETING_REPROMPT"])
        
        session_attributes["quiz_started"] = False
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
            )

class YesNoIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (is_intent_name("AMAZON.YesIntent")(handler_input) or
                is_intent_name("AMAZON.NoIntent")(handler_input))
    
    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        session_attributes = handler_input.attributes_manager.session_attributes
        quiz_started = session_attributes["quiz_started"]
        
        if is_intent_name("AMAZON.YesIntent")(handler_input) and not quiz_started:
            current_question_index = 0
            question = quiz_data[current_question_index]["q"]
            options = quiz_data[current_question_index]["o"]
            correct_answer = quiz_data[current_question_index]["a"]
            random.shuffle(options)
            a = options[0]
            b = options[1]
            c = options[2]
            d = options[3]
            correct_option = options_key[options.index(quiz_data[current_question_index]["a"])]
            
            speech_output = random.choice(language_prompts["FIRST_QUESTION"]).format(question,a,b,c,d)
            reprompt = random.choice(language_prompts["FIRST_QUESTION_REPROMPT"])
            
            session_attributes["current_question_index"] = current_question_index
            session_attributes["question"] = question
            session_attributes["options"] = options
            session_attributes["correct_option"] = correct_option
            session_attributes["correct_answer"] = correct_answer
            session_attributes["score"] = 0
            session_attributes["quiz_started"] = True
        
        elif is_intent_name("AMAZON.YesIntent")(handler_input) and quiz_started:
            speech_output = random.choice(language_prompts["QUIZ_IN_PROGRESS"])
            reprompt = random.choice(language_prompts["ANSWER_REPROMPT"])
        
        else:
            speech_output = random.choice(language_prompts["NO_RESPONSE"])
            return (
                handler_input.response_builder
                    .speak(speech_output)
                    .set_should_end_session(True)
                    .response
            )
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
            )

class AnswerIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AnswerIntent")(handler_input)
    
    def handle(self,handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        session_attributes = handler_input.attributes_manager.session_attributes
        
        users_choice = handler_input.request_envelope.request.intent.slots["answer"].resolutions.resolutions_per_authority[0].values[0].value.name
        correct_answer = session_attributes["correct_answer"]
        correct_option = session_attributes["correct_option"]
        score = session_attributes["score"]
        if users_choice.lower().strip() == correct_answer.lower().strip() or users_choice.lower().strip() == correct_option.lower().strip():
            speech_output = random.choice(language_prompts["CORRECT_ANSWER"])
            session_attributes["score"] += 1
        else:
            speech_output = random.choice(language_prompts["INCORRECT_ANSWER"]).format(correct_option,correct_answer)

        reprompt = random.choice(language_prompts["ANSWER_REPROMPT"])
        current_question_index = session_attributes["current_question_index"] + 1
        
        if current_question_index < 5:
            question = quiz_data[current_question_index]["q"]
            options = quiz_data[current_question_index]["o"]
            correct_answer = quiz_data[current_question_index]["a"]
            random.shuffle(options)
            a = options[0]
            b = options[1]
            c = options[2]
            d = options[3]
            correct_option = options_key[options.index(quiz_data[current_question_index]["a"])]
            
            next_question_speech = random.choice(language_prompts["NEXT_QUESTION"]).format(question,a,b,c,d)
            speech_output += next_question_speech
            
            session_attributes["current_question_index"] = current_question_index
            session_attributes["question"] = question
            session_attributes["options"] = options
            session_attributes["correct_option"] = correct_option
            session_attributes["correct_answer"] = correct_answer
        else:
            speech_output += random.choice(language_prompts["QUIZ_ENDED"]).format(session_attributes["score"],session_attributes["score"]*10)
            return(
                handler_input.response_builder
                    .speak(speech_output)
                    .set_should_end_session(True)
                    .response
            )
        return(
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
            )

class CancelOrStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))
    
    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        speech_output = random.choice(language_prompts["CANCEL_STOP_RESPONSE"])
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .set_should_end_session(True)
                .response
            )

class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.HelpIntent")(handler_input)
    
    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        speech_output = random.choice(language_prompts["HELP"])
        reprompt = random.choice(language_prompts["HELP_REPROMPT"])
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
            )

# This handler handles utterances that can't be matched to any other intent handler.
class FallbackIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)
    
    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        speech_output = random.choice(language_prompts["FALLBACK"])
        reprompt = random.choice(language_prompts["FALLBACK_REPROMPT"])
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
            )

class SessionEndedRequesthandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("SessionEndedRequest")(handler_input)
    
    def handle(self, handler_input):
        logger.info("Session ended with the reason: {}".format(handler_input.request_envelope.request.reason))
        return handler_input.response_builder.response

# Exception Handlers

# This exception handler handles syntax or routing errors. If you receive an error stating 
# the request handler is not found, you have not implemented a handler for the intent or 
# included it in the skill builder below
class CatchAllExceptionHandler(AbstractExceptionHandler):
    
    def can_handle(self, handler_input, exception):
        return True
    
    def handle(self, handler_input, exception):
        logger.error(exception, exc_info=True)
        
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        
        speech_output = language_prompts["ERROR"]
        reprompt = language_prompts["ERROR_REPROMPT"]
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
            )

# Interceptors

# This interceptor logs each request sent from Alexa to our endpoint.
class RequestLogger(AbstractRequestInterceptor):

    def process(self, handler_input):
        logger.debug("Alexa Request: {}".format(
            handler_input.request_envelope.request))

# This interceptor logs each response our endpoint sends back to Alexa.
class ResponseLogger(AbstractResponseInterceptor):

    def process(self, handler_input, response):
        logger.debug("Alexa Response: {}".format(response))

# This interceptor is used for supporting different languages and locales. It detects the users locale,
# loads the corresponding language prompts and sends them as a request attribute object to the handler functions.
class LocalizationInterceptor(AbstractRequestInterceptor):

    def process(self, handler_input):
        locale = handler_input.request_envelope.request.locale
        logger.info("Locale is {}".format(locale))
        
        try:
            with open("languages/"+str(locale)+".json") as language_data:
                language_prompts = json.load(language_data)
        except:
            with open("languages/"+ str(locale[:2]) +".json") as language_data:
                language_prompts = json.load(language_data)
        
        handler_input.attributes_manager.request_attributes["_"] = language_prompts


# Skill Builder
# Define a skill builder instance and add all the request handlers,
# exception handlers and interceptors to it.

sb = SkillBuilder()
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(AnswerIntentHandler())
sb.add_request_handler(YesNoIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequesthandler())

sb.add_exception_handler(CatchAllExceptionHandler())

sb.add_global_request_interceptor(LocalizationInterceptor())
sb.add_global_request_interceptor(RequestLogger())
sb.add_global_response_interceptor(ResponseLogger())

lambda_handler = sb.lambda_handler()