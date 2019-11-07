# elasticsearch-aggregator

## Usage

### Installation
1. Build image
```sh
docker build -t quay.io/<username>/elasticsearch-aggregator:latest .
docker push quay.io/<username>/elasticsearch-aggregator:latest
```
2. If needed, make the image registry public
3. Edit sre-agg-job.yaml with your updated image path above
4. If needed, edit sre-agg-job.yaml to change the namespace where the ES stack is installed
4. `oc create` the job

### Retrieving logs
```sh
oc get pods --sort-by='{.metadata.creationTimestamp}' -l job-name=sre-es-agg -n openshift-logging -o name |\
  tail -n1 | awk -F/ '{print $2}' | xargs -n1 oc logs -n openshift-logging
```
