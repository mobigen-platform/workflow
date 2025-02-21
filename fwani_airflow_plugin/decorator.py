import os
import pickle
from functools import wraps

from airflow.operators.python import get_current_context


def xcom_decorator(func):
    """airflow 기본 방식 (64KB 제한이 있음)"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        context = get_current_context()
        ti = context['ti']

        task = ti.task
        upstream_tasks = task.upstream_list
        downstream_tasks = task.downstream_list

        is_first_task = len(list(upstream_tasks)) == 0
        if is_first_task:
            print(f"‼️ 처음 태스크임.")
            before_task_outputs = []
            for t_id in kwargs.get("before_task_ids", []):
                before_task_outputs.append(ti.xcom_pull(task_ids=t_id, key="output"))
            input_data = before_task_outputs
        else:
            input_data = kwargs.get("input_data")

        result = func(input_data, *args, **kwargs)

        is_last_task = len(list(downstream_tasks)) == 0
        if is_last_task:
            print(f"‼️ 마지막 태스크임. output = {result}")
        else:
            ti.xcom_push(key="output", value=result)
        return result

    return wrapper


def rabbitmq_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


def file_decorator(func):
    """파일 기반 데이터 전달 (대용량 지원)"""
    # ✅ 파일 저장 경로 설정 (Airflow 컨테이너 내부 공유 가능하도록 설정)
    base_dir = "/tmp/airflow_data"
    os.makedirs(base_dir, exist_ok=True)

    @wraps(func)
    def wrapper(*args, **kwargs):
        context = get_current_context()
        ti = context['ti']

        task = ti.task
        upstream_tasks = task.upstream_list
        downstream_tasks = task.downstream_list

        is_first_task = len(list(upstream_tasks)) == 0
        task_id = task.task_id
        file_path = os.path.join(base_dir, f"{task_id}.pkl")

        if is_first_task:
            print(f"‼️ 처음 태스크 실행: {task_id}")
            input_data = None  # 처음 실행되는 태스크는 input_data 없음
        else:
            print(f"📥 {task_id} → 이전 Task 데이터 로드 중...")
            before_task_outputs = []
            for t_id in kwargs.get("before_task_ids", []):
                prev_file_path = os.path.join(base_dir, f"{t_id}.pkl")
                if os.path.exists(prev_file_path):
                    with open(prev_file_path, "rb") as f:
                        before_task_outputs.append(pickle.load(f))
                else:
                    print(f"⚠️ {prev_file_path} 파일 없음. 이전 Task 실행이 완료되지 않았을 수 있음.")
            input_data = before_task_outputs

        # ✅ 실제 UDF 실행
        result = func(input_data, *args, **kwargs)

        # ✅ 결과를 파일에 저장
        with open(file_path, "wb") as f:
            pickle.dump(result, f)
        print(f"📤 {task_id} → 결과 저장: {file_path}")

        is_last_task = len(list(downstream_tasks)) == 0
        if is_last_task:
            print(f"‼️ 마지막 태스크 완료: {task_id} → output = {result}")

        return result

    return wrapper
