import xmltodict
from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

DELIVERY_CODES_DICT = {"FedEx": {"Delivered": "DL", "In Transit": "IT", "Departed": "DP"}}


def populate_missing(key_name: str, data: dict) -> None:
    """
    Check whether key value is populated, if not added 'No information' placeholder

    :param key_name: key value to look for
    :param data: Dict which contains the data
    :return:
    """
    if key_name not in data:
        data[key_name] = "No information"


def xml_to_json(xml_response: str) -> dict:
    """
    Converts a xml response to a json object

    :param xml_response: XML data to parse
    :return: parsed delivery info for given track number
    """
    root = xmltodict.parse(xml_response)
    tracking_info = dict()
    track_details = root['SOAP-ENV:Envelope']['SOAP-ENV:Body']['TrackReply']['CompletedTrackDetails']['TrackDetails']

    if track_details["Notification"]["Severity"] == "ERROR":
        return {"error": track_details["Notification"]["LocalizedMessage"]}

    # Place to create dict to look for names of different in-company names to unified one, FDXG -> FedEx
    tracking_info["carrier"] = "FedEx"
    tracking_info["delivered"] = track_details["StatusDetail"]["Code"] == DELIVERY_CODES_DICT["FedEx"]["Delivered"]

    for date_event in track_details["DatesOrTimes"]:
        if date_event["Type"] == "ESTIMATED_DELIVERY":
            tracking_info["estimated_delivery"] = date_event["DateOrTimestamp"]

    populate_missing("estimated_delivery", tracking_info)

    for date_event in track_details["DatesOrTimes"]:
        if date_event["Type"] == "ACTUAL_DELIVERY":
            tracking_info["delivery_date"] = date_event["DateOrTimestamp"]

    populate_missing("delivery_date", tracking_info)

    tracking_info["tracking_number"] = track_details["TrackingNumber"]
    tracking_info["status"] = track_details["StatusDetail"]["Description"]
    tracking_info["tracking_stage"] = track_details["StatusDetail"]["Code"]

    tracking_info["checkpoints"] = list()

    for event in track_details["Events"]:
        event_loc = event["Address"]
        parsed_event_loc = {"city": event_loc.get("City", None),
                            "country": event_loc.get("CountryName", None),
                            "postal_code": event_loc.get("PostalCode", None),
                            "state": event_loc.get("StateOrProvinceCode", None)}

        event_data = {"description": event.get("EventDescription", None),
                      "location": parsed_event_loc,
                      "time": event["Timestamp"]}
        tracking_info["checkpoints"].append(event_data)

    return tracking_info


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/track', methods=['POST'])
def track():
    tracking_number = request.form['tracking_number']

    fedex_url = "https://wsbeta.fedex.com/web-services"
    headers = {
        "Content-Type": "text/xml",
    }

    with open("request_xml.xml", "r") as xml_file:
        xml_request = xml_file.read()

    xml_request = xml_request.replace("TRACKING_NUMBER_PLACEHOLDER", tracking_number)

    try:
        print("sending the request with tracking number", tracking_number)
        response = requests.post(fedex_url, data=xml_request, headers=headers)

        if response and response.status_code == 200:
            print("received the response with status code", response.status_code)
            json_response = xml_to_json(response.text)
            return jsonify(json_response)
        else:
            print(response.status_code, "mocking the response from the file")
            with open("fedex_mock_(1).xml", "r") as xml_file:
                json_response = xml_to_json(xml_file.read())
            return jsonify(json_response)
    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == '__main__':
    app.run(debug=True)
