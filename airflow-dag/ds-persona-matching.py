from airflow.kubernetes import secret
from airflow.kubernetes.secret import Secret
from airflow.operators.bash import BashOperator
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from airflow.operators.dummy import DummyOperator
from airflow.models.variable import Variable
from airflow import DAG
from datetime import datetime
from kubernetes.client.models import V1LocalObjectReference

image = "mashrequae.azurecr.io/persona-matching-engine:20293"

'''
{
"table_name": "PERSONA_CUSTOMER_DETAILS_TEMP4",
"schema_name": "curation_corp_dev"
"staging_table": "PERSONA_FUZZY_OUTPUT_1"
"staging_schema": "curation_corp_dev"
}

'''

connection_string = Variable.get('hive_secret')
principle_id = Variable.get('AML_PRINCIPAL_ID')
principle_pass = Variable.get('AML_PRINCIPAL_PASS')
tenant_id = Variable.get('AML_TENANT_ID')

table_in = "{{ dag_run.conf['table_name'] }}"
schema_in = "{{ dag_run.conf['schema_name'] }}"
st_tbl = "{{ dag_run.conf['staging_table'] }}"
st_sch = "{{ dag_run.conf['staging_schema'] }}"

with DAG(
    dag_id='ds-persona-matching',
    schedule_interval = None,
    start_date = datetime(year=2022,month=2,day=27),
    tags=['APP',"PERSONA"],
    catchup=False
) as dag:
    start =  DummyOperator(task_id='Start')
    k = KubernetesPodOperator(
        name='generate_matches',
        task_id='generate_matches',
        namespace='airflow-cluster',
        image = image,
        env_vars={'hive_secret':connection_string,
                  'AML_PRINCIPAL_ID':principle_id,
                  'AML_PRINCIPAL_PASS':principle_pass,
                  'AML_TENANT_ID':tenant_id},
        cmds = ["python", "main.py", "--table_name",table_in, "--schema_name", schema_in, "--staging_table", st_tbl, "--staging_schema", st_sch],
        image_pull_secrets=[V1LocalObjectReference('docker-secret')],
        service_account_name='airflow-cluster'
    )
start >> k
