export type HeritageTopic = "material" | "craftsmanship" | "brand_history";

export type Product = {
  id: string;
  qrValue: string;
  brandName: string;
  productName: string;
  summary: string;
  imageUrl: string;
};

export type ProductSummary = Product;

export type HeritageItem = {
  id: string;
  topic: HeritageTopic;
  title: string;
  content: string;
  sourceTitle: string;
  sourceUrl: string | null;
};

export type HeritageResponse = {
  productId: string;
  items: HeritageItem[];
};

export type Source = {
  title: string;
  url: string | null;
};

export type DocentStoryResponse = {
  sessionId: string;
  title: string;
  story: string;
  suggestedQuestions: string[];
  sources: Source[];
};

export type DocentMessageResponse = {
  messageId: string;
  answer: string;
  grounded: boolean;
  sources: Source[];
  suggestedQuestions: string[];
};

export type ApiErrorBody = {
  error?: {
    code?: string;
    message?: string;
  };
};
