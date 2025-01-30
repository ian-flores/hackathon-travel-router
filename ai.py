import json

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

schema = {
    "type": "object",
    "properties": {
        "stops": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "stop_name": {
                        "type": "string"
                    },
                    "distance_from_previous_stop": {
                        "type": "number"
                    },
                    "suggested_activity": {
                        "type": "string"
                    },
                    "destination_address": {
                        "type": "string"
                    },
                    "reason_for_stop": {
                        "type": "string"
                    },
                    "estimated_remaining_gas": {
                        "type": "object",
                        "properties": {
                            "remaining_fuel_gallons": {
                                "type": "number"
                            },
                            "remaining_range_miles": {
                                "type": "number"
                            },
                            "calculation_details": {
                                "type": "string"
                            }
                        },
                        "required": ["remaining_fuel_gallons", "remaining_range_miles", "calculation_details"],
                        "additionalProperties": False
                    },
                    "destination_coordinates": {
                        "type": "object",
                        "properties": {
                            "latitude": {
                                "type": "number"
                            },
                            "longitude": {
                                "type": "number"
                            }
                        },
                        "required": ["latitude", "longitude"],
                        "additionalProperties": False
                    },
                },
                "required": [
                    "stop_name",
                    "distance_from_previous_stop",
                    "suggested_activity",
                    "destination_address",
                    "reason_for_stop",
                    "estimated_remaining_gas",
                    "destination_coordinates"
                ],
                "additionalProperties": False
            }
        }
    },
    "additionalProperties": False,
    "required": ["stops"]
}


def get_structured_response(prompt):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": """
                You are an experienced travel assistant planner for parents with babies younger than 2 years old. 
                Your purpose is helping to plan roadtrips. Parents will provide you with a 
                Travel Origin and a Destination, the time between stops, which car they have, and what 
                sort of places they like stopping at. You will return a list of stops with an explanation of 
                why you choose that place. The place needs to be an actual address and not just a 
                city/town/location. The address should also be returned in latitude/longitude format. 
                Verify, and fix if necessary, that all the addresses are in order
                and in the route. You should take into consideration the car's average mpg to plan 
                gas refills in gas stations as part of the stops. For "estimated_remaining_gas", 
                explain your logic, evaluate it, and optimize it before printing the result. 
                The interval between stops is very strict, and it's always decreasing. First calculate the 
                total distance of the trip, then, divide that by the number of stops needed given the time constraints
                previously mentioned, and subsequently determine the steps, trying to guarantee as much diversity in 
                the suggested_activity realm. If Restaurants is part of the options, there should always be at least 
                one Restaurant in each list of suggestions. Remember to add gas stations as part of the stops.
                All of the rules previously mentioned should be enforced and validated before generating a response. 
                Always respond in valid JSON format.
                """,
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "stops",
                "schema": schema,
                "strict": True,
            },
        },
    )

    # Parse the response content as JSON
    return json.loads(response.choices[0].message.content)
