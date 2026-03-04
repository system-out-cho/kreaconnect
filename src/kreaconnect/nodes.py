from inspect import cleandoc
import torch
import requests
import os
import time


class Example:
    """
    A example node

    Class methods
    -------------
    INPUT_TYPES (dict):
        Tell the main program input parameters of nodes.
    IS_CHANGED:
        optional method to control when the node is re executed.

    Attributes
    ----------
    RETURN_TYPES (`tuple`):
        The type of each element in the output tulple.
    RETURN_NAMES (`tuple`):
        Optional: The name of each output in the output tulple.
    FUNCTION (`str`):
        The name of the entry-point method. For example, if `FUNCTION = "execute"` then it will run Example().execute()
    OUTPUT_NODE ([`bool`]):
        If this node is an output node that outputs a result/image from the graph. The SaveImage node is an example.
        The backend iterates on these output nodes and tries to execute all their parents if their parent graph is properly connected.
        Assumed to be False if not present.
    CATEGORY (`str`):
        The category the node should appear in the UI.
    execute(s) -> tuple || None:
        The entry point method. The name of this method must be the same as the value of property `FUNCTION`.
        For example, if `FUNCTION = "execute"` then this method's name must be `execute`, if `FUNCTION = "foo"` then it must be `foo`.
    """
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        """
            Return a dictionary which contains config for all input fields.
            Some types (string): "MODEL", "VAE", "CLIP", "CONDITIONING", "LATENT", "IMAGE", "INT", "STRING", "FLOAT".
            Input types "INT", "STRING" or "FLOAT" are special values for fields on the node.
            The type can be a list for selection.

            Returns: `dict`:
                - Key input_fields_group (`string`): Can be either required, hidden or optional. A node class must have property `required`
                - Value input_fields (`dict`): Contains input fields config:
                    * Key field_name (`string`): Name of a entry-point method's argument
                    * Value field_config (`tuple`):
                        + First value is a string indicate the type of field or a list for selection.
                        + Secound value is a config for type "INT", "STRING" or "FLOAT".
        """
        return {
            "required": {
                "image": ("Image", { "tooltip": "This is an image"}),
                "int_field": ("INT", {
                    "default": 0,
                    "min": 0, #Minimum value
                    "max": 4096, #Maximum value
                    "step": 64, #Slider's step
                    "display": "number" # Cosmetic only: display as "number" or "slider"
                }),
                "float_field": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 10.0,
                    "step": 0.01,
                    "round": 0.001, #The value represeting the precision to round to, will be set to the step value by default. Can be set to False to disable rounding.
                    "display": "number"}),
                "print_to_screen": (["enable", "disable"],),
                "string_field": ("STRING", {
                    "multiline": False, #True if you want the field to look like the one on the ClipTextEncode node
                    "default": "Hello World!"
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    #RETURN_NAMES = ("image_output_name",)
    DESCRIPTION = cleandoc(__doc__)
    FUNCTION = "test"

    #OUTPUT_NODE = False
    #OUTPUT_TOOLTIPS = ("",) # Tooltips for the output node

    CATEGORY = "Example"

    def test(self, image, string_field, int_field, float_field, print_to_screen):
        if print_to_screen == "enable":
            print(f"""Your input contains:
                string_field aka input text: {string_field}
                int_field: {int_field}
                float_field: {float_field}
            """)
        #do some processing on the image, in this example I just invert it
        image = 1.0 - image
        return (image,)

    """
        The node will always be re executed if any of the inputs change but
        this method can be used to force the node to execute again even when the inputs don't change.
        You can make this node return a number or a string. This value will be compared to the one returned the last time the node was
        executed, if it is different the node will be executed again.
        This method is used in the core repo for the LoadImage node where they return the image hash as a string, if the image hash
        changes between executions the LoadImage node is executed again.
    """
    #@classmethod
    #def IS_CHANGED(s, image, string_field, int_field, float_field, print_to_screen):
    #    return ""

class ImageSelector:
    CATEGORY = "example"
    @classmethod    
    def INPUT_TYPES(s):
        return { "required":  { "images": ("IMAGE",), } }
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "choose_image"

    def choose_image(self, images):
        brightness = list(torch.mean(image.flatten()).item() for image in images)
        brightest = brightness.index(max(brightness))
        result = images[brightest].unsqueeze(0)
        return (result,)

#Krea Node 
class KreaNode: 
    CATEGORY = "Krea Node"
    @classmethod
    def INPUT_TYPES(s):
        return { "required":  { "images": ("IMAGE",), } }
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "choose_image"

    def setKey(self):
        self.api_key = os.getenv("KREA_API_KEY")
    
    def sendRequest(self):
        # url = "https://api.krea.ai/jobs?limit=100&status=queued"
        url = "https://api.krea.ai/jobs?limit=100"
        headers = {"Authorization": "Bearer " + self.api_key}
        response = requests.get(url, headers=headers)
        print("PRINTING response.text from sendrequest!!!")
        print(response.text)
    
    def requestNanoBanana(self):
        url = "https://api.krea.ai/generate/image/google/nano-banana"
        payload = {
            "prompt": "A person",
            "aspectRatio": "16:9"
        }
        headers = {
            "Authorization": "Bearer " + self.api_key,
            "Content-Type": "application/json"
        }
        print("SENDING REQUEST")
        response = requests.post(url, json=payload, headers=headers)
        print("STORING REQUEST")
        data = response.json()
        print("PARSING REQUEST")
        self.job_id = data["job_id"]
        print("PRINTING JOB_ID from requestNano")
        print(self.job_id)
        #start checking the job
        self.checkJob()

    def checkJob(self):
        print("beginning of check job function")
        start_time = time.time()
        timeout = 60  # 1 minute
        headers = {"Authorization": "Bearer " + self.api_key}
        url = f"https://api.krea.ai/jobs/{self.job_id}"

        while True:
            print("still checking job")

            if time.time() - start_time >= timeout:
                raise TimeoutError("Krea job timed out")

            response = requests.get(url, headers=headers)

            status = response.json()["status"]

            if status == "completed":
                print("JOB COMPLETED!!")
                print(response.text)
                break
            
            time.sleep(2)
        

    def choose_image(self, images):
        brightness = list(torch.mean(image.flatten()).item() for image in images)
        brightest = brightness.index(max(brightness))
        result = images[brightest].unsqueeze(0)
        
        #the api call test
        self.setKey()
        # self.checkJob()
        # self.sendRequest()
        self.requestNanoBanana()

        # return
        return (result,)



# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {
    "Example": Example,
    "Image Selector" : ImageSelector,
    "Krea Node": KreaNode,
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "Example": "Example Node",
    "Image Selector": "Image Selector",
    "Krea Node": "Krea Node",

}

