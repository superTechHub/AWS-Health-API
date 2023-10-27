import json
import boto3

# Initialize the Boto3 clients
health_client = boto3.client('health')
sns_client = boto3.client('sns')

# SNS topic ARN where you want to publish event details
sns_topic_arn = 'YOUR_SNS_TOPIC_ARN'

def lambda_handler(event, context):
    try:
        # Describe Health Events
        events_response = health_client.describe_events(
            filter={
                'eventStatusCodes': ['open'],
                'eventTypeCategories': ['issue'],
                'services': ['EC2']
            },
            maxResults=10  # You can adjust this as needed
        )

        # Process and collect event details
        event_details = []
        for event in events_response.get('events', []):
            event_id = event.get('arn')
            event_description = event.get('eventDescription')
            event_affected_entities = health_client.describe_affected_entities(
                eventArns=[event_id]
            ).get('entities', [])

            event_details.append({
                'EventID': event_id,
                'Description': event_description,
                'AffectedEntities': event_affected_entities
            })

        if event_details:
            # Publish event details to the SNS topic
            sns_client.publish(
                TopicArn=sns_topic_arn,
                Message=json.dumps(event_details, indent=2),
                Subject='EC2 Health Events'
            )
        else:
            print("No relevant EC2 health events found.")

        return {
            'statusCode': 200,
            'body': json.dumps('Function executed successfully!')
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        raise e

# # Test event to invoke the Lambda function (you can modify this)
# test_event = {
#     "key1": "value1",
#     "key2": "value2"
# }

# Uncomment the next line for local testing (remove it when deploying to Lambda)
# lambda_handler(test_event, None)
