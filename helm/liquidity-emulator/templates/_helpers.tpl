{{/* vim: set filetype=mustache: */}}
{{/*
Expand the name of the chart.
*/}}
{{- define "liquidity.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "liquidity.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "liquidity.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "liquidity.labels" -}}
helm.sh/chart: {{ include "liquidity.chart" . }}
{{ include "liquidity.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "liquidity.selectorLabels" -}}
app.kubernetes.io/name: {{ include "liquidity.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "liquidity.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "liquidity.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{- define "liquidity.database.url" -}}
{{- if .Values.database.create }}
{{- $host := printf "%s-db" (include "liquidity.fullname" .) }}
{{- with .Values.database }}
{{- .protocol }}://{{ .username }}:{{ .password }}@{{ $host }}:{{ .port }}/{{ .dbName }}
{{- end }}
{{- else }}
{{- .Values.database.host }}
{{- end }}
{{- end }}

{{/*
Returns proper value for the LP's CUSTODY_PRIVATE_KEYS environment variable
*/}}
{{- define "liquidity.custodyPrivateKeys" }}
{{-     $privateKey := required "Wallet VASP account private key must be set in .Values.vaspPrivateKey" .Values.vaspPrivateKey }}
{{-     dict .Values.custodyWalletAccountName $privateKey | toJson | quote }}
{{- end }}
