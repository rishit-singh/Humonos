from tinytune.prompt import prompt_job
from tinytune.contexts.gptcontext import Any, GPTContext
from tinytune.pipeline import Pipeline
import json
import re


class DispatchAgent:
    @staticmethod
    def OnGenerate(content: Any):
        if content:
            print(content, end="")

    def __init__(self, model: str, apiKey: str):
        self.Context: GPTContext = GPTContext(model, apiKey)
        self.Events: list[dict] = [
            {"action": "SET_ALTITUDE", "args": {"altitude": 50}},
            {"action": "START_SCANNING", "args": {"scan_type": "infrared"}},
            {"action": "NAVIGATE", "args": {"destination": "pickup_point"}},
            {"action": "GRAB_OBJECT", "args": {"object_id": "package_123"}},
            {"action": "NAVIGATE", "args": {"destination": "delivery_point"}},
            {"action": "RELEASE_OBJECT", "args": {"object_id": "package_123"}},
            {"action": "NAVIGATE", "args": {"destination": "base"}},
        ]

        self.Pipeline: Pipeline | None = None
        self.SystemPrompt: str = f"""
            You are an agent that is the brain of an autonomous drone and takes all decisions for it based on the provided user input. You have access to a fixed amount of
            events that you can dispatch when needed to perform a certain task. You have the ability to chain the events you dispatch. To dispatch an event you output JSON in format
            {{ \"action\": "ACTION", "args": {{ "arg": "value" }} }}. Dispatch responses must always follow this format along with a the separate text that goes with it to let the user know what's
            going on. Make sure to put the text before the event dispatch objects. Avoid common mistakes like outputting the events with a '```json' prefix. You are supposed to create a chain of
            events when the user asks for multiple things in one sentence.
            You have access to the following events: {json.dumps(self.Events)}
        """
        self.Context.OnGenerate = DispatchAgent.OnGenerate

    def SendEvents(self):
        return

    def Setup(self):
        def Init(context: GPTContext):
            return context.Prompt({"role": "system", "content": self.SystemPrompt}).Run(
                stream=True
            )

        @prompt_job(id="prompt")
        def Prompt(id: str, context: GPTContext, prevResult, prompt: dict):
            return (
                context.Prompt({"role": "user", "content": str(prompt["prompt"])})
                .Run(stream=True)
                .Messages[-1]
            )

        @prompt_job(id="parse")
        def Parse(id: str, context: GPTContext, prevResult: dict, obj):
            def ParseResponse(response: str):
                match = re.findall(r"({[^}]+}|\[[^\]]+\])", response)

                if match:
                    matched_str = "".join(match)
                    return (response[0 : response.find(matched_str)], match)

                return (response, None)

            res = ParseResponse(dict(prevResult)["content"])

            print("response: ", res)

            return res

        Init(self.Context)

        self.Pipeline = Pipeline[dict](self.Context).AddJob(Prompt).AddJob(Parse)

    def Run(self):
        if not (self.Pipeline):
            raise Exception("Main pipeline is None.")

        while True:
            prompt: str = input("> ")

            self.Pipeline.Run(stream=True, prompt=prompt)

    def __call__(self):
        if not (self.Pipeline):
            self.Setup()

        self.Run()
