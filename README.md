# Python mini project with kubernetes-client/python

A mini project to hang aroung with python and kubernetes-client/python.

This is an exporter that can run either inside the cluster or from outside pointing to a kubeconfig and exports persistent volumes that in various states. 

## Intentions

If your storageclass has the `reclaimPolicy: Retain`, it's useful once your deployment crashes because your volumes will still retain in your cluster. The downside however is, that this might blow up your storage backends due to "orphaned" volumes.

The exporter fetches volumes from the cluster with their `name`, their `state` and their `creation_timestamp`. You then can fetch metrics and create alerts via Prometheus if a volume is released and older than a desired amount of days. 


## Testing with kind


```bash
cat <<EOF | kind create cluster --config=-
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  kubeadmConfigPatches:
  - |
    kind: InitConfiguration
    nodeRegistration:
      kubeletExtraArgs:
        node-labels: "ingress-ready=true"
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
    protocol: TCP
  - containerPort: 443
    hostPort: 443
    protocol: TCP
EOF
```

## Kubernetes compatibility

See the python-sdk compatibility list at [https://github.com/kubernetes-client/python#compatibility](https://github.com/kubernetes-client/python#compatibility)
