import re
import long_responses as long
import speech_recognition as sr
import pyttsx3
import questions

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Initialize speech recognizer
r = sr.Recognizer()


def speak(text):
    """Uses text-to-speech to say the given text."""
    engine.say(text)
    engine.runAndWait()


def take_command():
    """Listens for audio input and returns the recognized text."""
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=1)
        print("Listening...")
        audio = r.listen(source)
        try:
            print("Recognizing...")
            recognized_text = r.recognize_google(audio, language="en-in")
            print(f"User said: {recognized_text}")
            return recognized_text
        except sr.UnknownValueError:
            return "Sorry, I did not understand that."
        except sr.RequestError:
            return "Sorry, there was a problem with the request."


def message_probability(user_message, recognised_words, single_response=False, required_words=[]):
    """Calculates the probability of a message matching the given words."""
    message_certainty = 0
    has_required_words = True

    # Count how many words from the recognized words list are present in the user message
    for word in user_message:
        if word in recognised_words:
            message_certainty += 1

    # Calculate the percentage of recognized words in the user message
    percentage = float(message_certainty) / float(len(recognised_words))

    # Check if all required words are in the user message
    for word in required_words:
        if word not in user_message:
            has_required_words = False
            break

    # Return the certainty score if required words are present or if it's a single response
    if has_required_words or single_response:
        return int(percentage * 100)
    else:
        return 0


def check_all_messages(message):
    """Checks all predefined messages and finds the best match."""
    highest_prob_list = {}

    # Simplifies response creation / adds it to the dict
    def response(bot_response, list_of_words, single_response=False, required_words=None):
        if required_words is None:
            required_words = []
        nonlocal highest_prob_list
        highest_prob_list[bot_response] = message_probability(message, list_of_words, single_response, required_words)

    # Responses -------------------------------------------------------------------------------------------------------
    words = questions.get_list_of_words()
    for i in range(len(questions.questions)):
        response(bot_response=questions.answers[i], list_of_words=words[i])

    response('Hello!', ['hello', 'hi', 'hey', 'sup', 'heyo'], single_response=True)
    response('See you!', ['bye', 'goodbye'], single_response=True)
    response('I\'m doing fine, and you?', ['how', 'are', 'you', 'doing'], required_words=['how'])
    response('You\'re welcome!', ['thank', 'thanks'], single_response=True)
    response('Thank you!', ['i', 'love', 'code', 'palace'], required_words=['code', 'palace'])

    # Longer responses
    response(long.R_ADVICE, ['give', 'advice'], required_words=['advice'])
    response(long.R_EATING, ['what', 'you', 'eat'], required_words=['you', 'eat'])

    # Find the best match from the responses
    best_match = max(highest_prob_list, key=highest_prob_list.get)

    return long.unknown() if highest_prob_list[best_match] < 1 else best_match


def get_response(input_message):
    """Processes the user input and returns the appropriate response."""
    split_message = re.split(r'\s+|[,;?!.-]\s*', input_message.lower())
    response = check_all_messages(split_message)
    return response


# Main loop for continuous listening and responding
while True:
    command_input = take_command()  # Renamed for clarity
    response_from_bot = get_response(command_input)
    print('Bot: ' + response_from_bot)
    speak(response_from_bot)

