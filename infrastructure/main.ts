import { Construct } from "constructs";
import { App, TerraformStack, TerraformOutput } from "cdktf";
import { OciProvider } from "./.gen/providers/oci/provider";
import { FunctionsApplication } from "./.gen/providers/oci/functions-application";
import { FunctionsFunction } from "./.gen/providers/oci/functions-function";
import { CoreVcn } from "./.gen/providers/oci/core-vcn";
import { CoreSubnet } from "./.gen/providers/oci/core-subnet";
import { CoreInternetGateway } from "./.gen/providers/oci/core-internet-gateway";
import { CoreRouteTable } from "./.gen/providers/oci/core-route-table";
import { CoreSecurityList } from "./.gen/providers/oci/core-security-list";
import * as dotenv from "dotenv";

// Load environment variables
dotenv.config();

interface DbrxToAtpStackConfig {
  compartmentId: string;
  region: string;
  tenancyOcid: string;
  userOcid: string;
  fingerprint: string;
  privateKeyPath: string;
  ocirRepository: string; // e.g., "phx.ocir.io/<namespace>/dbrx-to-atp"
  vcnCidr?: string;
  subnetCidr?: string;
}

class DbrxToAtpStack extends TerraformStack {
  constructor(scope: Construct, name: string, config: DbrxToAtpStackConfig) {
    super(scope, name);

    // OCI Provider
    new OciProvider(this, "oci", {
      region: config.region,
      tenancyOcid: config.tenancyOcid,
      userOcid: config.userOcid,
      fingerprint: config.fingerprint,
      privateKeyPath: config.privateKeyPath,
    });

    // VCN for Functions
    const vcn = new CoreVcn(this, "functions-vcn", {
      compartmentId: config.compartmentId,
      cidrBlocks: [config.vcnCidr || "10.0.0.0/16"],
      displayName: "dbrx-to-atp-vcn",
      dnsLabel: "dbrxtoatp",
    });

    // Internet Gateway
    const internetGateway = new CoreInternetGateway(this, "internet-gateway", {
      compartmentId: config.compartmentId,
      vcnId: vcn.id,
      displayName: "dbrx-to-atp-igw",
      enabled: true,
    });

    // Route Table
    const routeTable = new CoreRouteTable(this, "route-table", {
      compartmentId: config.compartmentId,
      vcnId: vcn.id,
      displayName: "dbrx-to-atp-rt",
      routeRules: [
        {
          networkEntityId: internetGateway.id,
          destination: "0.0.0.0/0",
          destinationType: "CIDR_BLOCK",
        },
      ],
    });

    // Security List
    const securityList = new CoreSecurityList(this, "security-list", {
      compartmentId: config.compartmentId,
      vcnId: vcn.id,
      displayName: "dbrx-to-atp-sl",
      egressSecurityRules: [
        {
          destination: "0.0.0.0/0",
          protocol: "all",
          stateless: false,
        },
      ],
      ingressSecurityRules: [
        {
          protocol: "6", // TCP
          source: "0.0.0.0/0",
          stateless: false,
          tcpOptions: {
            min: 443,
            max: 443,
          },
        },
      ],
    });

    // Subnet for Functions
    const subnet = new CoreSubnet(this, "functions-subnet", {
      compartmentId: config.compartmentId,
      vcnId: vcn.id,
      cidrBlock: config.subnetCidr || "10.0.1.0/24",
      displayName: "dbrx-to-atp-subnet",
      dnsLabel: "functions",
      routeTableId: routeTable.id,
      securityListIds: [securityList.id],
      prohibitPublicIpOnVnic: false,
    });

    // NOTE: Policy creation commented out - requires tenancy-level permissions
    // You may need to manually create these policies or ask your administrator:
    // 1. Allow service faas to read repos in compartment id ${config.compartmentId}
    // 2. Allow service faas to use virtual-network-family in compartment id ${config.compartmentId}
    // 3. Allow dynamic-group dbrx-to-atp-fn-dg to read autonomous-databases in compartment id ${config.compartmentId}
    // 4. Allow dynamic-group dbrx-to-atp-fn-dg to read secret-family in compartment id ${config.compartmentId}

    // Functions Application
    const app = new FunctionsApplication(this, "functions-app", {
      compartmentId: config.compartmentId,
      displayName: "dbrx-to-atp-app",
      subnetIds: [subnet.id],
      config: {
        // Add any application-level configuration here
      },
    });

    // Note: OCI Functions deployment requires Docker image push to OCIR
    // This is typically done via fn CLI or CI/CD pipeline
    // The CDKTF creates the infrastructure, but deployment is separate

    // Functions Function
    const fn = new FunctionsFunction(this, "migration-function", {
      applicationId: app.id,
      displayName: "dbrx-to-atp-migration",
      image: config.ocirRepository + ":latest",
      memoryInMbs: "512",
      timeoutInSeconds: 300,
      config: {
        // Environment variables for the function
        // IMPORTANT: Use OCI Vault/Secrets for sensitive data in production
      },
    });

    // Outputs
    new TerraformOutput(this, "function-id", {
      value: fn.id,
      description: "OCI Function ID",
    });

    new TerraformOutput(this, "function-invoke-endpoint", {
      value: fn.invokeEndpoint,
      description: "Function Invoke Endpoint URL",
    });

    new TerraformOutput(this, "application-id", {
      value: app.id,
      description: "Functions Application ID",
    });

    new TerraformOutput(this, "vcn-id", {
      value: vcn.id,
      description: "VCN ID",
    });

    new TerraformOutput(this, "subnet-id", {
      value: subnet.id,
      description: "Subnet ID",
    });

    // Output information for OIC integration
    new TerraformOutput(this, "oic-integration-info", {
      value: JSON.stringify({
        compartmentId: config.compartmentId,
        functionId: fn.id,
        invokeEndpoint: fn.invokeEndpoint,
        region: config.region,
      }),
      description: "Information needed for OIC integration",
    });
  }
}

// Main app
const app = new App();

// Read configuration from environment variables
const stackConfig: DbrxToAtpStackConfig = {
  compartmentId: process.env.OCI_COMPARTMENT_ID || "",
  region: process.env.OCI_REGION || "us-phoenix-1",
  tenancyOcid: process.env.OCI_TENANCY_OCID || "",
  userOcid: process.env.OCI_USER_OCID || "",
  fingerprint: process.env.OCI_FINGERPRINT || "",
  privateKeyPath: process.env.OCI_PRIVATE_KEY_PATH || "~/.oci/oci_api_key.pem",
  ocirRepository: process.env.OCIR_REPOSITORY || "",
  vcnCidr: process.env.VCN_CIDR,
  subnetCidr: process.env.SUBNET_CIDR,
};

new DbrxToAtpStack(app, "dbrx-to-atp-infrastructure", stackConfig);

app.synth();
