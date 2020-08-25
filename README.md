# signalfx_billing_summary
This script is for informational purposes only.
## Usage
### virtualenv
Create a virtualenv and install the required dependencies:
```
pip install -r signalfx_billing_summary/requirements.txt
```
### Running the script that pulls directly from SignalFx:
> python signalfx_billing_summary/billing_and_usage_summary.py --token TOKEN --filename FILENAME --realm REALM --month MONTH <br/>
> FILENAME is the name that should be used for the output file<br/>
> MONTH For example: January
<br/>
### Running the script after you've downloaded the file locally:
> python signalfx_billing_summary/billing_and_usage_local.py --input_file INPUT_FILENAME --output_file OUTPUT_FILENAME <br/>
> INPUT_FILENAME is the name of the file that you've downloaded locally <br/>
> OUTPUT_FILENAME is the name that should be used for the output file <br/>