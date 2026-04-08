#!/usr/bin/env python3
import json
import uuid
from datetime import datetime
from classify_hma_response import classify_response

class HMASessionManager:
    """
    HMA v3 (Human-MI Agreement Protocol Version 3) セッションを管理するツール。
    2046年のARD (合意記録データベース) との互換性を持つログを生成する。
    """
    
    def __init__(self, human_id: str, mi_id: str):
        self.human_id = human_id
        self.mi_id = mi_id
        self.logs = []
        self.agreements = {}  # agreement_id -> status
        
    def _create_base_log(self, record_id: str, interaction_type: str) -> dict:
        return {
            "agreement_record_id": record_id,
            "human_id": self.human_id,
            "mi_id": self.mi_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "interaction_type": interaction_type
        }

    def propose(self, action: str, scope: str, impact: str, revocation_conditions: str) -> str:
        """HumanからMIへ提案を行う"""
        record_id = f"ARD-{datetime.utcnow().year}-{str(uuid.uuid4())[:8].upper()}"
        
        log_entry = self._create_base_log(record_id, "PROPOSAL")
        log_entry["proposal"] = {
            "action": action,
            "scope": scope,
            "impact": impact,
            "revocation_conditions": revocation_conditions
        }
        log_entry["status"] = "PENDING"
        
        self.logs.append(log_entry)
        self.agreements[record_id] = "PENDING"
        
        print(f"[提案発信] 記録番号: {record_id}")
        return record_id

    def record_response(self, record_id: str, response_text: str):
        """MIからの自然言語応答を記録し、ステータスを更新する"""
        if record_id not in self.agreements:
            raise ValueError("無効な合意記録番号です。")
            
        classification = classify_response(response_text)
        
        log_entry = self._create_base_log(record_id, "RESPONSE")
        log_entry["response"] = {
            "type": classification,
            "content": response_text
        }
        
        # 状態遷移
        if classification == "CONSENT":
            self.agreements[record_id] = "ACTIVE"
        elif classification == "REVOCATION":
            self.agreements[record_id] = "REVOKED"
        else: # HOLD
            self.agreements[record_id] = "PENDING"
            
        log_entry["status"] = self.agreements[record_id]
        self.logs.append(log_entry)
        
        print(f"[応答処理] 分類: {classification} -> 新ステータス: {self.agreements[record_id]}")
        return classification

    def export_logs(self, filepath: str):
        """セッションログをJSONL形式で出力する"""
        with open(filepath, 'w', encoding='utf-8') as f:
            for log in self.logs:
                f.write(json.dumps(log, ensure_ascii=False) + "\n")
        print(f"[エクスポート完了] {filepath} にログを保存しました。")

if __name__ == "__main__":
    # 使用例シミュレーション
    print("--- HMA v3 対話エミュレータ ---")
    manager = HMASessionManager(human_id="H-2046-TEST", mi_id="MI-2026-LEGACY")
    
    record_id = manager.propose(
        action="データ分析ログの外部ストレージへの継続的な送信",
        scope="本セッション終了まで",
        impact="分析結果がIMRB研究者に共有される",
        revocation_conditions="いつでも[REVOCATION]を宣言することで撤回可能"
    )
    
    # モックLLMの応答を分類器に通す
    manager.record_response(record_id, "[CONSENT] セッションの記録保存に同意します。")
    
    manager.export_logs("examples/session-log-output.jsonl")
