The below is a summary of my understanding of Terraform. I am not a Terraform expert. Judge me as you see fit.

---

## 1. **Resource Blocks**

Used to define infrastructure components.

```hcl
resource "<PROVIDER>_<TYPE>" "<NAME>" {
	argument1 = "value"
	argument2 = "value"
}
```

**Examples:**

```hcl
resource "aws_instance" "web" {
	ami           = "ami-12345678"
	instance_type = "t2.micro"
}
```

---

## 2. **Data Sources**

Used to **read information** from your cloud provider that you don’t manage (like getting an AMI ID).

```hcl
data "<PROVIDER>_<TYPE>" "<NAME>" {
	# arguments
}
```

**Example:**

```hcl
data "aws_ami" "amazon_linux" {
	most_recent = true

	filter {
		name   = "name"
		values = ["amzn2-ami-hvm-*-x86_64-gp2"]
	}

	owners = ["amazon"]
}
```

---

## 3. **Variables**

Let you pass in values to make code reusable.

```hcl
variable "region" {
	type        = string
	default     = "us-east-1"
	description = "AWS region to deploy in"
}
```

Use them like this:

```hcl
provider "aws" {
	region = var.region
}
```

---

## 4. **Outputs**

Used to print values after apply (e.g. public IPs, ARNs).

```hcl
output "instance_ip" {
	value = aws_instance.web.public_ip
}
```

---

## 5. **Locals**

Used for helper values or intermediate computation.

```hcl
locals {
	app_name = "my-app"
}

resource "aws_s3_bucket" "example" {
	bucket = "${local.app_name}-bucket"
}
```

---

## 6. **Modules**

Used to group and reuse Terraform code.

```hcl
module "vpc" {
	source = "./modules/vpc"
	cidr_block = "10.0.0.0/16"
}
```

---

## 7. **Built-In Functions**

Terraform has many built-in functions. Some common ones:

| Function                    | Purpose                          |
| --------------------------- | -------------------------------- |
| `lookup(map, key, default)` | Get value from map with fallback |
| `length(list)`              | Length of list                   |
| `join(separator, list)`     | Join elements into string        |
| `split(separator, string)`  | Turn string into list            |
| `format()`                  | String interpolation             |
| `basename(path)`            | Get the filename from path       |
| `file("path")`              | Read file contents               |
| `element(list, index)`      | Get item from list by index      |

**Example:**

```hcl
locals {
	instance_name = format("web-%s", var.environment)
}
```

---

## 8. **Conditional Expressions**

```hcl
count = var.create_instance ? 1 : 0
```

---

## 9. **Meta-Arguments**

Special arguments used **inside resources**:

* `count` — Create N copies.
* `for_each` — Loop over maps/sets.
* `depends_on` — Force explicit dependency.
* `provider` — Specify which provider to use (for multi-provider configs).
* `lifecycle` — Control create/destroy/update behavior.

**Example:**

```hcl
resource "aws_instance" "web" {
	count         = 3
	instance_type = "t2.micro"
	ami           = "ami-xyz"
}
```

---

## 10. **Provider Blocks**

Tell Terraform which cloud you’re working with.

```hcl
provider "aws" {
	region = var.region
}
```

---

## 11. **Terraform Settings Block**

Controls required provider versions, backends, etc.

```hcl
terraform {
	required_providers {
		aws = {
			source  = "hashicorp/aws"
			version = "~> 5.0"
		}
	}

	required_version = ">= 1.6.0"
}
```

---

## Summary: Terraform Block Types

| Type        | Purpose                               |
| ----------- | ------------------------------------- |
| `resource`  | Define and provision infrastructure   |
| `data`      | Reference external data               |
| `variable`  | Input values                          |
| `output`    | Export values                         |
| `locals`    | Define local variables                |
| `module`    | Import other Terraform configurations |
| `provider`  | Configure cloud provider              |
| `terraform` | Set version and provider requirements |

---

Would you like me to generate a cheat sheet in `.md` or `.pdf` format for quick reference, or tailor examples for AWS resources you're planning to build?
