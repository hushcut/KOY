import type {
  ApiErrorBody,
  DocentMessageResponse,
  DocentStoryResponse,
  HeritageResponse,
  HeritageTopic,
  Product,
  ProductSummary,
} from "@/types/api";

const API_URL = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(/\/$/, "");

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;

  try {
    response = await fetch(`${API_URL}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...init?.headers,
      },
    });
  } catch {
    throw new ApiError("백엔드 서버에 연결할 수 없습니다. 서버 실행 상태를 확인해 주세요.", "NETWORK_ERROR", 0);
  }

  if (!response.ok) {
    const body = (await response.json().catch(() => ({}))) as ApiErrorBody;
    throw new ApiError(
      body.error?.message ?? "요청을 처리하지 못했습니다. 잠시 후 다시 시도해 주세요.",
      body.error?.code ?? "UNKNOWN_ERROR",
      response.status,
    );
  }

  return response.json() as Promise<T>;
}

export function getProductByQr(qrValue: string) {
  return request<Product>(`/products/by-qr/${encodeURIComponent(qrValue)}`);
}

export function searchProducts(query: string) {
  return request<{ items: ProductSummary[] }>(`/products/search?q=${encodeURIComponent(query)}`);
}

export function getProductHeritage(productId: string) {
  return request<HeritageResponse>(`/products/${encodeURIComponent(productId)}/heritage`);
}

export function createDocentStory(productId: string, interest: HeritageTopic) {
  return request<DocentStoryResponse>("/docent/story", {
    method: "POST",
    body: JSON.stringify({ productId, interest }),
  });
}

export function sendDocentMessage(sessionId: string, question: string) {
  return request<DocentMessageResponse>(`/docent/sessions/${encodeURIComponent(sessionId)}/messages`, {
    method: "POST",
    body: JSON.stringify({ question }),
  });
}
