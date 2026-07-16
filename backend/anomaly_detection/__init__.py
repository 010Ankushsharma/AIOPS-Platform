"""Anomaly Detection Service - Statistical and ML-based detection."""
import numpy as np
from typing import Optional
from dataclasses import dataclass
from enum import Enum
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN
from scipy import stats
import structlog

logger = structlog.get_logger()


class AnomalyType(str, Enum):
    SPIKE = "spike"
    DROP = "drop"
    TREND = "trend"
    SEASONALITY = "seasonality"
    OUTLIER = "outlier"


@dataclass
class AnomalyResult:
    is_anomaly: bool
    confidence: float
    anomaly_type: Optional[AnomalyType]
    description: str
    metric_name: str
    value: float
    expected_range: tuple[float, float]


class StatisticalDetector:
    """Statistical anomaly detection using Z-score and moving averages."""

    def __init__(self, z_threshold: float = 3.0, window_size: int = 30):
        self.z_threshold = z_threshold
        self.window_size = window_size

    def detect_zscore(self, values: np.ndarray, metric_name: str = "") -> list[AnomalyResult]:
        """Detect anomalies using Z-score method."""
        results = []
        if len(values) < 10:
            return results

        mean = np.mean(values)
        std = np.std(values)
        if std == 0:
            return results

        z_scores = np.abs((values - mean) / std)
        
        for i, (z, val) in enumerate(zip(z_scores, values)):
            if z > self.z_threshold:
                anomaly_type = AnomalyType.SPIKE if val > mean else AnomalyType.DROP
                results.append(AnomalyResult(
                    is_anomaly=True,
                    confidence=min(z / (self.z_threshold * 2), 1.0),
                    anomaly_type=anomaly_type,
                    description=f"Z-score {z:.2f} exceeds threshold {self.z_threshold}",
                    metric_name=metric_name,
                    value=val,
                    expected_range=(mean - 2 * std, mean + 2 * std),
                ))
        return results

    def detect_moving_average(self, values: np.ndarray, metric_name: str = "") -> list[AnomalyResult]:
        """Detect anomalies using moving average deviation."""
        results = []
        if len(values) < self.window_size + 5:
            return results

        moving_avg = np.convolve(values, np.ones(self.window_size) / self.window_size, mode="valid")
        moving_std = np.array([
            np.std(values[max(0, i - self.window_size):i])
            for i in range(self.window_size, len(values))
        ])

        for i in range(len(moving_avg)):
            idx = i + self.window_size
            deviation = abs(values[idx] - moving_avg[i])
            if moving_std[i] > 0 and deviation > 3 * moving_std[i]:
                results.append(AnomalyResult(
                    is_anomaly=True,
                    confidence=min(deviation / (4 * moving_std[i]), 1.0),
                    anomaly_type=AnomalyType.SPIKE if values[idx] > moving_avg[i] else AnomalyType.DROP,
                    description=f"Value deviates {deviation:.2f} from moving average",
                    metric_name=metric_name,
                    value=values[idx],
                    expected_range=(moving_avg[i] - 2 * moving_std[i], moving_avg[i] + 2 * moving_std[i]),
                ))
        return results


class MLDetector:
    """Machine learning-based anomaly detection."""

    def __init__(self, contamination: float = 0.05):
        self.contamination = contamination
        self.isolation_forest = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100,
        )

    def detect_isolation_forest(self, data: np.ndarray, metric_name: str = "") -> list[AnomalyResult]:
        """Detect anomalies using Isolation Forest."""
        results = []
        if len(data) < 20:
            return results

        if data.ndim == 1:
            data = data.reshape(-1, 1)

        self.isolation_forest.fit(data)
        predictions = self.isolation_forest.predict(data)
        scores = self.isolation_forest.score_samples(data)

        for i, (pred, score) in enumerate(zip(predictions, scores)):
            if pred == -1:
                confidence = min(abs(score) / 0.5, 1.0)
                results.append(AnomalyResult(
                    is_anomaly=True,
                    confidence=confidence,
                    anomaly_type=AnomalyType.OUTLIER,
                    description=f"Isolation Forest anomaly score: {score:.4f}",
                    metric_name=metric_name,
                    value=float(data[i][0]) if data.ndim > 1 else float(data[i]),
                    expected_range=(float(np.percentile(data, 5)), float(np.percentile(data, 95))),
                ))
        return results

    def detect_dbscan(self, data: np.ndarray, eps: float = 0.5, min_samples: int = 5) -> list[AnomalyResult]:
        """Detect anomalies using DBSCAN clustering."""
        results = []
        if len(data) < min_samples + 5:
            return results

        if data.ndim == 1:
            data = data.reshape(-1, 1)

        # Normalize
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        data_scaled = scaler.fit_transform(data)

        clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(data_scaled)
        labels = clustering.labels_

        for i, label in enumerate(labels):
            if label == -1:  # Noise point = anomaly
                results.append(AnomalyResult(
                    is_anomaly=True,
                    confidence=0.75,
                    anomaly_type=AnomalyType.OUTLIER,
                    description="DBSCAN noise point detected",
                    metric_name="",
                    value=float(data[i][0]),
                    expected_range=(float(np.percentile(data, 10)), float(np.percentile(data, 90))),
                ))
        return results


class ThresholdDetector:
    """Simple threshold-based detection with configurable rules."""

    def __init__(self):
        self.rules: dict[str, dict] = {}

    def add_rule(self, metric_name: str, warning: float, critical: float, direction: str = "above"):
        """Add a threshold rule for a metric."""
        self.rules[metric_name] = {
            "warning": warning,
            "critical": critical,
            "direction": direction,
        }

    def detect(self, metric_name: str, value: float) -> Optional[AnomalyResult]:
        """Check value against thresholds."""
        rule = self.rules.get(metric_name)
        if not rule:
            return None

        is_above = rule["direction"] == "above"
        
        if (is_above and value >= rule["critical"]) or (not is_above and value <= rule["critical"]):
            return AnomalyResult(
                is_anomaly=True,
                confidence=0.95,
                anomaly_type=AnomalyType.SPIKE if is_above else AnomalyType.DROP,
                description=f"Critical threshold breached: {value} {'>' if is_above else '<'} {rule['critical']}",
                metric_name=metric_name,
                value=value,
                expected_range=(0, rule["warning"]) if is_above else (rule["warning"], float("inf")),
            )
        elif (is_above and value >= rule["warning"]) or (not is_above and value <= rule["warning"]):
            return AnomalyResult(
                is_anomaly=True,
                confidence=0.70,
                anomaly_type=AnomalyType.SPIKE if is_above else AnomalyType.DROP,
                description=f"Warning threshold breached: {value}",
                metric_name=metric_name,
                value=value,
                expected_range=(0, rule["warning"]) if is_above else (rule["warning"], float("inf")),
            )
        return None


class AnomalyDetectionService:
    """Orchestrates multiple anomaly detection strategies."""

    def __init__(self):
        self.statistical = StatisticalDetector()
        self.ml = MLDetector()
        self.threshold = ThresholdDetector()
        self._setup_default_thresholds()

    def _setup_default_thresholds(self):
        self.threshold.add_rule("cpu_percent", warning=80.0, critical=95.0)
        self.threshold.add_rule("memory_percent", warning=85.0, critical=95.0)
        self.threshold.add_rule("disk_percent", warning=80.0, critical=90.0)
        self.threshold.add_rule("error_rate", warning=5.0, critical=10.0)
        self.threshold.add_rule("latency_p99_ms", warning=500.0, critical=2000.0)
        self.threshold.add_rule("container_restarts", warning=3.0, critical=10.0)

    def analyze(self, metric_name: str, values: np.ndarray) -> list[AnomalyResult]:
        """Run all detection methods and merge results."""
        results = []
        
        # Statistical methods
        results.extend(self.statistical.detect_zscore(values, metric_name))
        results.extend(self.statistical.detect_moving_average(values, metric_name))
        
        # ML methods
        results.extend(self.ml.detect_isolation_forest(values, metric_name))
        
        # Threshold check on latest value
        if len(values) > 0:
            threshold_result = self.threshold.detect(metric_name, float(values[-1]))
            if threshold_result:
                results.append(threshold_result)
        
        # Deduplicate and sort by confidence
        results.sort(key=lambda r: r.confidence, reverse=True)
        return results
