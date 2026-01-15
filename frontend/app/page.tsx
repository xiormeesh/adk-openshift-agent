"use client";

import { CopilotKit } from "@copilotkit/react-core";
import { CopilotPopup } from "@copilotkit/react-ui";
import "@copilotkit/react-ui/styles.css";

export default function Home() {
  return (
    <CopilotKit
      runtimeUrl="/api/copilotkit"
      agent="openshift_assistant"
    >
      <main className="min-h-screen bg-gradient-to-b from-gray-900 to-gray-800">
        <div className="container mx-auto px-4 py-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            OpenShift AI Assistant
          </h1>
          <p className="text-gray-400">
            Use the chat in the bottom-right corner to interact with your cluster
          </p>
        </div>
        <CopilotPopup
          instructions="You are an expert Kubernetes and OpenShift assistant."
          labels={{
            title: "OpenShift Assistant",
            initial: "Hi! I can answer questions about Kubernetes and OpenShift.",
          }}
        />
      </main>
    </CopilotKit>
  );
}
