#!/bin/bash
set -e

echo "🚀 Запуск развертывания Docker Counter App в Kind..."

cd ~/docker-counter-project

# Удаляем старый кластер, если есть
if kind get clusters | grep -q docker-counter; then
    echo "📦 Удаляем старый кластер..."
    kind delete cluster --name docker-counter
fi

# Создаем новый кластер
echo "🐳 Создаем новый Kind кластер..."
kind create cluster --name docker-counter --config kind-config.yaml

# Устанавливаем Helm чарт
echo "📦 Устанавливаем Helm чарт..."
cd helm-chart
helm install docker-counter . --set image.repository=romanvercetti/docker-counter --set image.tag=latest
cd ..

echo ""
echo "✅ Развертывание завершено!"
echo "📍 Приложение доступно: http://localhost:8080"
echo ""
echo "Для просмотра статуса:"
echo "  kubectl get pods"
echo "  kubectl get svc"
echo ""
echo "Для удаления кластера:"
echo "  kind delete cluster --name docker-counter"
