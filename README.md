# Tube Map Update Alerts
Twitter bot to alert you of when the London Tube map changes.
Uses Google Cloud Functions to check
[Transport for London's website](https://tfl.gov.uk/maps/track) for changes to
the Tube map, and archives these versions in a Google Cloud Storage bucket.

## Setting Up
1. Clone the repo (`git clone https://github.com/retnikt/tubemapupdatealerts`)
2. [Create][1] a Twitter Developer account if you don't have one already, and set up
a Twitter app and generate your credentials
3. Put the credentials in `twitter_credentials.example.json` and rename the file
to `twitter_credentials.json`
4. [Create][2] a Google Cloud Platform account if you don't have one already, create
a project, and enable billing
5. [Install][3] the Google Cloud SDK and ensure you have the `gcloud` command on
your `PATH`
6. Ensure the Pub/Sub, Scheduler, Storage, and Functions APIs are enabled on
your project
7. [Create][4] a Google Cloud Storage bucket and a Service Account with the
Storage Object Admin role to access it. Choose an appropriate region (do not use
multi-region or dual-region), uniform access control, and the Standard storage
class.
8. Put the name of the bucket in `bucket_name.example.txt` and rename the file
to `bucket_name.txt`
9. Create a Pub/Sub topic in your project using `gcloud pubsub topics create
{your topic name}`
10. [Create][5] a Cloud Scheduler job (use the same region that your Storage
Bucket is in), to target to the Pub/Sub topic you just created and payload of
just `*`. The frequency should be `*/15 * * * *` for every 15 minutes (you can 
customise it using the [Unix cron format][6])
9. Deploy the function to Google Cloud Functions using:
```bash
gcloud functions deploy tube_map_update_check \
 --trigger-topic={your topic name} \
 --project={your project name} \
 --service-account="{your_service_account name}@{your project name}.iam.gserviceaccount.com" \
 --region={your chosen location} \
 --runtime=python37
```
replacing `{your topic name}`,  `{your project name}`,
`{your service account name}`, and `{your bucket location}` with the names of
the Cloud Pub/Sub topic, the Project, and the Service Account that you created
in steps 5, 7, and 9, and the location you chose when you created your Storage
bucket. 

[1]: https://python-twitter.readthedocs.io/en/latest/getting_started.html#getting-your-application-tokens 
[2]: https://console.cloud.google.com/
[3]: https://cloud.google.com/sdk/docs/
[4]: https://cloud.google.com/storage/docs/creating-buckets
[5]: https://cloud.google.com/scheduler/docs/creating#creating_jobs
[6]: http://man7.org/linux/man-pages/man5/crontab.5.html
