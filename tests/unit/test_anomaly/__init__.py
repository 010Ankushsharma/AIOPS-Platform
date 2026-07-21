"""Unit tests for anomaly detection service."""
import numpy as np
import pytest
from backend.anomaly_detection import (
    AnomalyDetectionService, StatisticalDetector, MLDetector, ThresholdDetector
)


class TestStatisticalDetector:
    def setup_method(self):
        self.detector = StatisticalDetector(z_threshold=3.0)

    def test_zscore_detects_spike(self):
        values = np.concatenate([np.random.normal(50, 5, 100), [200]])
        results = self.detector.detect_zscore(values, "test_metric")
        assert len(results) > 0
        assert results[0].is_anomaly is True
        assert results[0].value == 200

    def test_zscore_no_anomaly_in_normal_data(self):
        values = np.random.normal(50, 5, 100)
        results = self.detector.detect_zscore(values, "test_metric")
        assert len(results) == 0

    def test_zscore_empty_data(self):
        results = self.detector.detect_zscore(np.array([]), "test_metric")
        assert results == []

    def test_moving_average_detects_deviation(self):
        values = np.concatenate([np.ones(50) * 10, [100], np.ones(10) * 10])
        results = self.detector.detect_moving_average(values, "test_metric")
        assert any(r.is_anomaly for r in results)


class TestMLDetector:
    def setup_method(self):
        self.detector = MLDetector(contamination=0.1)

    def test_isolation_forest_detects_outliers(self):
        normal = np.random.normal(0, 1, 100)
        outliers = np.array([10, -10, 15])
        data = np.concatenate([normal, outliers])
        results = self.detector.detect_isolation_forest(data, "test_metric")
        assert len(results) > 0

    def test_isolation_forest_small_data(self):
        data = np.array([1, 2, 3])
        results = self.detector.detect_isolation_forest(data, "test_metric")
        assert results == []

    def test_dbscan_detects_noise(self):
        cluster = np.random.normal(0, 0.5, (50, 1))
        outlier = np.array([[10], [-10]])
        data = np.vstack([cluster, outlier])
        results = self.detector.detect_dbscan(data.flatten())
        assert len(results) > 0


class TestThresholdDetector:
    def setup_method(self):
        self.detector = ThresholdDetector()
        self.detector.add_rule("cpu_percent", warning=80.0, critical=95.0)

    def test_critical_threshold_breach(self):
        result = self.detector.detect("cpu_percent", 97.0)
        assert result is not None
        assert result.is_anomaly is True
        assert result.confidence == 0.95

    def test_warning_threshold_breach(self):
        result = self.detector.detect("cpu_percent", 85.0)
        assert result is not None
        assert result.confidence == 0.70

    def test_no_breach(self):
        result = self.detector.detect("cpu_percent", 50.0)
        assert result is None

    def test_unknown_metric(self):
        result = self.detector.detect("unknown_metric", 100.0)
        assert result is None


class TestAnomalyDetectionService:
    def setup_method(self):
        self.service = AnomalyDetectionService()

    def test_analyze_with_spike(self):
        values = np.concatenate([np.random.normal(50, 5, 100), [200]])
        results = self.service.analyze("cpu_percent", values)
        assert len(results) > 0
        assert all(r.is_anomaly for r in results)

    def test_analyze_normal_data(self):
        values = np.random.normal(50, 2, 100)
        results = self.service.analyze("some_metric", values)
        # May detect some with ML, but should be minimal
        high_confidence = [r for r in results if r.confidence > 0.8]
        assert len(high_confidence) < 5
