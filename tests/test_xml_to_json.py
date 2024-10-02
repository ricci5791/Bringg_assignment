import pytest
from app import xml_to_json


@pytest.fixture
def sample_xml_response():
    """Simulate a FedEx tracking XML response."""
    return """
    <SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
        <SOAP-ENV:Body>
            <TrackReply>
                <CompletedTrackDetails>
                    <TrackDetails>
                        <TrackingNumber>122816215025810</TrackingNumber>
                        <StatusDetail>
                            <Code>DL</Code>
                            <Description>Delivered</Description>
                        </StatusDetail>
                        <DatesOrTimes>
                            <Type>ACTUAL_DELIVERY</Type>
                            <DateOrTimestamp>2024-09-09T11:19:36-07:00</DateOrTimestamp>
                        </DatesOrTimes>
                        <DatesOrTimes>
                            <Type>ACTUAL_PICKUP</Type>
                            <DateOrTimestamp>2024-09-05T00:00:00</DateOrTimestamp>
                        </DatesOrTimes>
                        <Events>
                            <EventDescription>Delivered</EventDescription>
                            <Timestamp>2024-09-27T14:00:00Z</Timestamp>
                            <Address>
                                <City>San Francisco</City>
                                <StateOrProvinceCode>CA</StateOrProvinceCode>
                                <PostalCode>94105</PostalCode>
                                <CountryName>United States</CountryName>
                            </Address>
                        </Events>
                        <Events>
                            <EventDescription>Shipped</EventDescription>
                            <Timestamp>2024-09-23T14:00:00Z</Timestamp>
                            <Address>
                                <City>Illinois</City>
                                <StateOrProvinceCode>IL</StateOrProvinceCode>
                                <PostalCode>55041</PostalCode>
                                <CountryName>United States</CountryName>
                            </Address>
                        </Events>
                    </TrackDetails>
                </CompletedTrackDetails>
            </TrackReply>
        </SOAP-ENV:Body>
    </SOAP-ENV:Envelope>
    """


@pytest.fixture
def expected_json_response():
    """Simulate the expected JSON/dict output from the xml_to_json function."""
    return {
        "carrier": "FedEx",
        "delivered": True,
        'delivery_date': '2024-09-09T11:19:36-07:00',
        'estimated_delivery': 'No information',
        "tracking_number": "122816215025810",
        "status": "Delivered",
        "tracking_stage": "DL",
        "checkpoints": [
            {
                "description": "Delivered",
                "location": {
                    "city": "San Francisco",
                    "country": "United States",
                    "postal_code": "94105",
                    "state": "CA"
                },
                "time": "2024-09-27T14:00:00Z"
            },
            {'description': 'Shipped',
             'location': {'city': 'Illinois',
                          'country': 'United States',
                          'postal_code': '55041',
                          'state': 'IL'},
             'time': '2024-09-23T14:00:00Z'
             },
        ]
    }


def test_xml_to_json(sample_xml_response, expected_json_response):
    """Test the xml_to_json function."""
    result = xml_to_json(sample_xml_response)
    assert result == expected_json_response
