import { NextRequest } from "next/server";
import {
  CopilotRuntime,
  ExperimentalEmptyAdapter,
  copilotRuntimeNextJSAppRouterEndpoint,
} from "@copilotkit/runtime";
import { HttpAgent } from "@ag-ui/client";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

// Empty adapter since we're only using one agent
const serviceAdapter = new ExperimentalEmptyAdapter();

// Create runtime with AG-UI HttpAgent pointing to ADK backend
const runtime = new CopilotRuntime({
  agents: {
    openshift_assistant: new HttpAgent({ url: `${BACKEND_URL}/` }),
  },
});

export const POST = async (req: NextRequest) => {
  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime,
    serviceAdapter,
    endpoint: "/api/copilotkit",
  });

  return handleRequest(req);
};
