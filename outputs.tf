output "lambda_function_name" {
  value = aws_lambda_function.iam_key_monitor.function_name
}

output "iam_role_arn" {
  value = aws_iam_role.lambda_role.arn
}

output "eventbridge_rule_name" {
  value = aws_cloudwatch_event_rule.daily_trigger.name
}