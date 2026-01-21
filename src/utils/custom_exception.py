import sys 
import traceback 

class CustomException(Exception):
    def _init_(self, error_message: str, error_detail:sys):
        super().__init__(error_message) 




"""
>> import sys #  to get sys.exc_info()-> its gave full context of traceback
>> class CustomException(Exception): # inherit from python base Exception + our own magic
>> def _init_(self, error_message: str, error_detail:sys): # error_message for hooman and error_detail to get whole traceback
>> __init__ (often called "dunder init") is the constructor or initializer method for a class. It is automatically called by Python every time you create a new instance (object) of that class
>> Important : If you use single underscores (_init_), Python will treat it as a regular method and will not call it automatically when you create a new object. You should change it to __init__ with two underscores on each side.
>> self: This is a required first parameter that represents the individual object being created. It allows the class to attach data to that specific instance.
>> error_message: str: This is a custom parameter you must provide when creating the object (e.g., MyError("Something went wrong", ...)). It expects a string value.
>> error_detail: sys: This is another custom parameter, likely intended to pass system-level error information (though usually typed as types.TracebackType or similar if using the sys module).
>> Initialization: Inside this method, you would typically assign these values to the object using self.error_message = error_message so the object "remembers" them later
>> super(): is a built-in Python function used to access and call methods from a parent class. It allows a child class to use the logic already written in the parent class, so you don't have to rewrite it.

>> super(): Look at the parent class.
   .__init__(): Run the parent's initialization method.
   (error_message): Give the parent the message so it knows what the error is. 
>> super().__init__(error_message) tells Python to send the error message up to the parent class so it can handle the basic setup for you.















"""